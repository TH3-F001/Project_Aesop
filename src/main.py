#!env/bin/python
import os.path

# from common.browser import WebBrowser
from src.infrastructure.api_clients.youtube_client import YoutubeUploader, YoutubeArgs
from src.infrastructure.api_clients.elevenlabs_client import Dictator
from src.infrastructure.api_clients.reddit_client import Reddit
from src.infrastructure.utils.content_scraper import Scraper
from src.application.exceptions.openai_exceptions import OpenAIRateLimitExceededException
from src.infrastructure.api_clients.chatgpt_client_old import ChatGPT
from src.infrastructure.utils.content_helper import Helper
from src.infrastructure.utils.content_editor import Editor
from time import sleep
from typing import Dict
import json


ROOT_OUTPUT_DIR = "data/output"
CREDENTIAL_DIR = "data/restricted"

def get_root_vidgen_instructions() -> str:
    print("\n Getting Root VidGen Instructions...")
    vidgen_prompt_path = "data/vidgen_assistant_prompt.txt"
    with open(vidgen_prompt_path, "r") as file:
        video_generator_prompt = file.read()

    return video_generator_prompt

#region Channels
def request_new_channel_input(name: str) -> dict:
    print(f"\nChannel: {name} is not registered. Please provide some additional information...")
    focus = input(f"Enter the channel: {name}'s focus: > ")
    mission = input(f"Enter the channel: {name}'s mission: > ")

    channel = {
        "channel_focus": focus,
        "channel_mission": mission,
        "thread_id": None
    }

    return channel


def channel_name_is_registered(name: str) -> bool:
    print(f"\nChecking if Channel: {name} is registered...")
    channels = get_channels()
    result = name in channels
    print(f"\tChannel: {name} Registered: {result}.")
    return result


def save_channels(channels_data: Dict[str, dict]) -> None:
    channels_path = "data/channels.json"
    with open(channels_path, "w") as file:
        json.dump(channels_data, file, indent=4)


def register_channel(new_channel_name: str, new_channel_data: dict) -> None:
    print(f"\nRegistering New Channel: {new_channel_name}")
    channels_data = get_channels()
    channels_data[new_channel_name] = new_channel_data
    save_channels(channels_data)
    print(f"\tChannel: {new_channel_name} Registered.")



def update_channel(channel_name: str, updated_channel_data: dict) -> None:
    print(f"\nUpdating Channel: {channel_name}")
    channels_data = get_channels()
    channels_data[channel_name] = updated_channel_data
    save_channels(channels_data)
    print(f"\tChannel: {channel_name} Updated.")


def check_and_register_channel(channel_name: str) -> None:
    if not channel_name_is_registered(channel_name):
        new_channel_data = request_new_channel_input(channel_name)
        register_channel(channel_name, new_channel_data)

def reset_channel_thread(channel_name: str):
    channel = get_channel(channel_name)
    if channel.get("thread_id") != None:
        channel["thread_id"] = None
        update_channel(channel_name, channel)

def get_channel_thread_id(chat: ChatGPT, channel_name: str):
    channel = get_channel(channel_name)
    thread_id = channel.get("thread_id")

    if thread_id is None:
        thread_id = chat.new_assistant_thread().id
        channel["thread_id"] = thread_id
        update_channel(channel_name, channel)
    return thread_id

#endregion

#region Get Config Data
def get_channel_directory(channel_name: str) -> str:
    global ROOT_OUTPUT_DIR
    filesafe_channel_name = Helper.make_string_filesafe(channel_name)
    channel_dir = f"{ROOT_OUTPUT_DIR}/{filesafe_channel_name}"
    return channel_dir

def get_video_directory(channel_name: str, video_name: str) -> str:
    channel_dir = get_channel_directory(channel_name)
    filesafe_video_name = Helper.make_string_filesafe(video_name)
    video_dir = f"{channel_dir}/{filesafe_video_name}"
    return video_dir

def get_channels() -> Dict[str, dict]:
    print("\nLoading channels.json...")
    channels_path = "data/channels.json"
    if not os.path.exists(channels_path):
        raise FileNotFoundError(f"Channel Config File couldnt be found: {channels_path}")
    with open(channels_path, "r") as file:
        config_dict = json.load(file)
    print("\tChannels Loaded.")
    return config_dict

def get_channel(channel_name: str) -> dict:
    channels = get_channels()
    return channels.get(channel_name)

def get_video_json(channel_name: str, video_name: str) -> dict:
    video_dir = get_video_directory(channel_name, video_name)
    filesafe_video_name = Helper.make_string_filesafe(video_name)
    video_json_path = f"{video_dir}/{filesafe_video_name}.json"
    if not os.path.exists(video_json_path):
        raise FileNotFoundError(f"Video Config File couldnt be found: {video_json_path}")
    with open(video_json_path) as file:
        video_dict = json.load(file)
    return video_dict


def get_video_property(property_name: str, channel_name:str, video_name:str):
    # Ensure property arg is valid
    approved_properties = {"Title", "Description", "Tags", "Pinned_Comment", "Script", "Image_Prompts"}
    if property_name not in approved_properties:
        raise ValueError(f"Requested property '{property_name}' is not valid. Approved properties are: {approved_properties}")

    video_json = get_video_json(channel_name, video_name)
    property = video_json.get(property_name)
    return property
#endregion


#region Utilities
def prepare_output_folders():
    channels = get_channels()
    for channel_name in channels.keys():
        channel_dir = get_channel_directory(channel_name)
        Helper.create_directory_structure(channel_dir)


def ensure_vidgen_assistant_exists(chat: ChatGPT, channel_name: str):
    if not chat.assistant_exists("VidGen Assistant"):
        reset_channel_thread(channel_name)
        root_vidgen_instructions = get_root_vidgen_instructions()
        chat.create_new_assistant("VidGen Assistant", root_vidgen_instructions)


def setup_thread(chat: ChatGPT, channel_name: str, source_material: str):
    # channel = get_channel(channel_name)
    # thread_id = get_channel_thread_id(chat, channel_name)
    thread = chat.new_assistant_thread()
    chat.generate_user_message(source_material, thread)
    return thread



def run_thread_with_retry(chat: ChatGPT, thread, channel_name, source_material):
    try:
        return run_assistant_thread(chat, thread, channel_name)
    except RateLimitExceededException:
        print("Thread Rate Limit Reached. Resetting Thread")
        reset_channel_thread(channel_name)
        new_thread = setup_thread(chat, channel_name, source_material)
        return run_assistant_thread(chat, new_thread, channel_name)


def run_assistant_thread(chat: ChatGPT, thread, channel_name):
    channel = get_channel(channel_name)
    channel_instructions = json.dumps(channel, indent=2)
    print("CHANNEL INSTRUCTIONS:", channel_instructions)
    return chat.run_assistant_thread(thread, "VidGen Assistant", channel_instructions)


def get_video_files(channel_name: str, video_name: str):
    video_dir = get_video_directory(channel_name, video_name)
    audio_clip_files = [os.path.join(video_dir, file) for file in os.listdir(video_dir) if '_audio_clip.mp4' in file]

    # Identify where video files are stored, and err out if not found
    if audio_clip_files:
        video_files = audio_clip_files
    else:
        audio_clips_dir = os.path.join(video_dir, 'audio_clips')
        if not os.path.exists(audio_clips_dir):
            raise FileNotFoundError(f"No 'audio_clips' directory found in {video_dir}")
        video_files = [os.path.join(audio_clips_dir, file) for file in os.listdir(audio_clips_dir) if file.endswith('.mp4')]

    # Ensure correct video order using script dict
    script_dict = get_video_property("Script", channel_name, video_name)
    ordered_video_files = []

    # Order video files based on the script dictionary
    for key in script_dict.keys():
        clip_title = Helper.make_string_filesafe(key)
        for filepath in video_files:
            if clip_title in os.path.basename(filepath):
                ordered_video_files.append(filepath)
                break

    return ordered_video_files

def organize_output_folder(channel_name: str, video_name: str):
    video_dir = get_video_directory(channel_name, video_name)
    image_dir = f"{video_dir}/images"
    audio_dir = f"{video_dir}/audio"
    sclips_dir = f"{video_dir}/silent_clips"
    aclips_dir = f"{video_dir}/audio_clips"
    Helper.create_directory_structure(image_dir)
    Helper.create_directory_structure(audio_dir)
    Helper.create_directory_structure(sclips_dir)
    Helper.create_directory_structure(aclips_dir)

    for filename in os.listdir(video_dir):
        file_path = f"{video_dir}/{filename}"
        if filename.endswith(".png"):
            Helper.move_file(file_path, image_dir)
        elif filename.endswith(".mp3"):
            Helper.move_file(file_path, audio_dir)
        elif "base_clip" in filename:
            Helper.move_file(file_path, sclips_dir)
        elif "audio_clip" in filename:
            Helper.move_file(file_path, aclips_dir)
        elif "_clip.mp4" in filename:
            os.remove(file_path)
#endregion


#region Primary Functions
# Gets a video idea from the VidGen Assistant (making the assistant and registering channels as needed)

def request_video_idea(chat: ChatGPT, channel_name: str, source_material: str):
    print("\nQuerying VidGen Assistant...")
    check_and_register_channel(channel_name)
    ensure_vidgen_assistant_exists(chat, channel_name)

    thread = setup_thread(chat, channel_name, source_material)
    result = run_thread_with_retry(chat, thread, channel_name, source_material)

    json_results = Helper.convert_string_to_json(result)
    video_dir_path = get_video_directory(channel_name, json_results["Title"])
    Helper.create_directory_structure(video_dir_path)
    file_path = f"{video_dir_path}/{Helper.make_string_filesafe(json_results['Title'])}.json"
    Helper.save_json_to_file(json_results, file_path)
    return json_results


def request_video_images(chat:ChatGPT, channel_name: str, video_name: str):
    print(f"\nGenerating Images for video: {video_name}...")
    video_json = get_video_json(channel_name, video_name)
    for img_name, img_prompt in video_json["Image_Prompts"].items():
        video_dir_path = get_video_directory(channel_name, video_json["Title"])
        img_path = f"{video_dir_path}/{Helper.make_string_filesafe(img_name)}.png"
        print(f"Generating {img_name}...")
        chat.generate_image(img_prompt, img_path)
    print(f"\t{video_name} Image Generation Complete!")


def request_video_voiceover(chat:ChatGPT, channel_name: str, video_name: str):
    print("\nGenerating ChatGPT Voiceover...")
    script = get_video_property("Script", channel_name, video_name)
    vid_dir = get_video_directory(channel_name, video_name)

    for scene_name, scene_script in script.items():
        filesafe_scene_name = Helper.make_string_filesafe(scene_name)
        out_path = f"{vid_dir}/{filesafe_scene_name}.mp3"
        chat.get_voice_from_text(scene_script, out_path)


def generate_video_from_assets(channel_name: str, video_name: str, style="zoom_in"):
    video_dir = get_video_directory(channel_name, video_name)
    filepaths = {}

    for filename in os.listdir(video_dir):
        if filename.endswith(".png"):
            base_filename = filename.split(".png")[0]
            base_filepath = f"{video_dir}/{filename}"
            new_filepath = f"{video_dir}/{base_filename}_base_clip.mp4"
            filepaths[base_filepath] = new_filepath

    for original_path, new_path in filepaths.items():
        print(f"\n\nImage_Path: {original_path}\nOutput_Path: {new_path}")
        audio_path = original_path.replace(".png", ".mp3")
        duration = Editor.get_mp3_duration(audio_path)
        Editor.create_video_from_image(original_path, new_path, duration, video_style=style)
        audio_out_path = new_path.replace("base_clip", "audio_clip")
        Editor.combine_audio_video(new_path, audio_path, audio_out_path)





def compile_video(channel_name, video_name):
    output_file = f"{get_video_directory(channel_name, video_name)}/{Helper.make_string_filesafe(video_name)}.mp4"
    video_files = get_video_files(channel_name, video_name)
    print(f"outputting {video_name} to {output_file}")
    Editor.concatenate_videos(video_files, output_file)




def main():
    ...
    # channel_name = "SpaceSecrets"
    #
    # chat = ChatGPT(f"{CREDENTIAL_DIR}/gpt_auth.json")
    # source_material = Helper.get_web_page("https://www.space.com/nasa-lasers-pet-photos-into-space")
    # print(source_material)
    #
    # cont = input("continue? y/n")
    # if cont != "y":
    #     exit(1)
    #
    # video_idea = request_video_idea(chat, channel_name, source_material)
    # video_title = video_idea.get("Title")
    #
    # request_video_images(chat, channel_name, video_title)
    # request_video_voiceover(chat, channel_name, video_title)
    # generate_video_from_assets(channel_name, video_title)
    # organize_output_folder(channel_name, video_title)
    # compile_video(channel_name, video_title)

    # #region ElevenLabs Test
    # elevenlabs_credpath = "data/restricted/elevenlabs_auth.json"
    # elevenlabs_voices_path = "data/elevenlabs_voices.json"
    # test_input_path = "data/output/Test/input_test.mp3"
    # dictator = Dictator(elevenlabs_credpath, elevenlabs_voices_path)
    # voice = "Nia Davis- Black Female"
    # out_path = "data/output/Test/soundfx.mp3"
    # text = "car crash"
    # dictator.text_to_sound_fx(text, out_path)
    # #endregion

    #region Reddit Test
    # cred_path = "data/restricted/reddit_auth.json"
    # reddit = Reddit(cred_path)
    # reddit.get_gilded_posts("test")
    # scraper = Scraper("data/restricted/newsapi_auth.json")
    # scraper.get_latest_news("space")


if __name__ == '__main__':
    # main()

    # visla = Visla()
    # visla.log_on()
    # visla.create_video()
    # visla.download_video()

    youtube_args = YoutubeArgs("/home/neon/Videos/OBS/hello_world.mp4",
                             "Hello World3.0",
                             "test video",
                             22,
                             "test, hello world",
                             "private")
    youtube = YoutubeUploader(youtube_args, aspect=(9,16))
    youtube.run()

