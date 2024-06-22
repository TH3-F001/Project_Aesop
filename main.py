#!env/bin/python

from common.browser import WebBrowser
from common.youtube import YoutubeUploader, YoutubeArgs
from common.chatgpt import ChatGPT
from common.visla import Visla
from common.content_helper import Helper
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


def get_channels() -> Dict[str, dict]:
    print("\nLoading channels.json...")
    channels_path = "appdata/prompts/gpt/channels.json"
    with open(channels_path, "r") as file:
        config_dict = json.load(file)
    print("\tChannels Loaded.")
    return config_dict


def get_channel(channel_name: str) -> dict:
    channels = get_channels()
    return channels.get(channel_name)


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


def prepare_output_folders():
    channels = get_channels()
    for channel_name, channel_data in channels.items():
        dir_name = Helper.make_string_filesafe(channel_name)
        Helper.create_directory_structure(f"{ROOT_OUTPUT_DIR}/{dir_name}")

#endregion


# Gets a video idea from the VidGen Assistant (making the assistant and registering channels as needed)

def query_vidgen_assistant(chat: ChatGPT, channel_name: str, source_material: str):
    print("\nQuerying VidGen Assistant...")
    check_and_register_channel(channel_name)

    if chat.assistant_exists("VidGen Assistant"):
        vidgen_prompt_assistant = chat.get_assistant("VidGen Assistant")
    else:
        root_vidgen_instructions = get_root_vidgen_instructions()
        vidgen_prompt_assistant = chat.create_new_assistant("VidGen Assistant", root_vidgen_instructions)

    channel = get_channel(channel_name)

    if channel["thread_id"] is None:
        thread = chat.new_assistant_thread()
        channel["thread_id"] = thread.id
        update_channel(channel_name, channel)
    else:
        thread = chat.get_thread_by_id(channel["thread_id"])

    chat.generate_user_message(source_material, thread)

    channel_instructions = json.dumps(get_channel(channel_name), indent=2)

    result = chat.run_assistant_thread(thread, vidgen_prompt_assistant, channel_instructions)
    json_results = Helper.convert_string_to_json(result)
    filesafe_filename = Helper.make_string_filesafe(json_results["Title"])
    filesafe_dirname = Helper.make_string_filesafe(channel_name)
    video_dir_path = f"{ROOT_OUTPUT_DIR}/{filesafe_dirname}/{filesafe_filename}"
    Helper.create_directory_structure(video_dir_path)
    file_path = f"{video_dir_path}/{filesafe_filename}"
    Helper.save_json_to_file(json_results, file_path)
    return json_results




def main():
    prepare_output_folders()
    channel_name = "SpaceSecrets"

    chat = ChatGPT()
    source_material = Helper.get_web_page("https://thespacereview.com/article/4808/1")
    # print(source_material)
    video_idea = query_vidgen_assistant(chat, channel_name, source_material)

    for img_name, img_prompt in video_idea["Image_Prompts"].items():
        safe_img_name = Helper.make_string_filesafe(img_name)
        safe_channel_name = Helper.make_string_filesafe(channel_name)
        safe_video_name = Helper.make_string_filesafe(video_idea["Title"])
        img_path = f"{ROOT_OUTPUT_DIR}/{safe_channel_name}/{safe_video_name}/{safe_img_name}"
        print(f"Generating {img_name}...")
        chat.generate_image(img_prompt, img_path)


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

