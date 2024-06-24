#!env/bin/python
import os.path

from common.browser import WebBrowser
from common.youtube import YoutubeUploader, YoutubeArgs
from common.exceptions import RateLimitExceededException
from common.chatgpt import ChatGPT
from common.visla import Visla
from common.content_helper import Helper
from common.content_editor import Editor
from time import sleep
from typing import Dict
import json


ROOT_OUTPUT_DIR = "appdata/output"


def get_root_vidgen_instructions() -> str:
    print("\n Getting Root VidGen Instructions...")
    vidgen_prompt_path = "appdata/prompts/gpt/vidgen_assistant_prompt.txt"
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
    channels_path = "appdata/prompts/gpt/channels.json"
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
    channels_path = "appdata/prompts/gpt/channels.json"
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
    channel = get_channel(channel_name)
    thread_id = get_channel_thread_id(chat, channel_name)
    thread = chat.get_thread_by_id(thread_id)
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
    return chat.run_assistant_thread(thread, "VidGen Assistant", channel_instructions)
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

def convert_video_images_to_clips(channel_name: str, video_name: str, style="zoom_in"):
    video_dir = get_video_directory(channel_name, video_name)
    filepaths = {}

    print(video_dir)
    for filename in os.listdir(video_dir):
        if filename.endswith(".png"):
            base_filename = filename.split(".png")[0]
            base_filepath = f"{video_dir}/{filename}"
            new_filepath = f"{video_dir}/{base_filename}_clip.mp4"
            filepaths[base_filepath] = new_filepath

    for original_path, new_path in filepaths.items():
        print(f"\n\nImage_Path: {original_path}\nOutput_Path: {new_path}")
        audio_path = original_path.replace(".png", ".mp3")
        duration = Editor.get_mp3_duration(audio_path)
        Editor.create_video_from_image(original_path, new_path, duration)




def main():
    channel_name = "SpaceSecrets"

    chat = ChatGPT()
    # source_material = Helper.get_web_page("https://thespacereview.com/article/4808/1")
    # video_idea = request_video_idea(chat, channel_name, source_material)
    # video_title = video_idea.get("Title")
    #
    # request_video_images(chat, channel_name, video_title)
    # request_video_voiceover(chat, channel_name, video_title)
    convert_video_images_to_clips(channel_name, "Hubble's Final Frontier: Surviving on a Single Gyro!")




if __name__ == '__main__':
    main()

    # visla = Visla()
    # visla.log_on()
    # visla.create_video()
    # visla.download_video()

    # youtube_args = YoutubeArgs("/home/neon/Videos/OBS/hello_world.mp4",
    #                          "Hello World3.0",
    #                          "test video",
    #                          22,
    #                          "test, hello world",
    #                          "private")
    # youtube = YoutubeUploader(youtube_args, aspect=(9,16))
    # youtube.run()

