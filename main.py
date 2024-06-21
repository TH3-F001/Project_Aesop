#!env/bin/python

from common.browser import WebBrowser
from common.youtube import YoutubeUploader, YoutubeArgs
from common.chatgpt import ChatGPT
from common.visla import Visla
from common.content_helper import Helper
from time import sleep
import yaml


ROOT_OUTPUT_DIR = "appdata/output"


def get_root_vidgen_instructions() -> str:
    print("\n Getting Root VidGen Instructions...")
    vidgen_prompt_path = "appdata/prompts/gpt/vidgen_assistant_prompt.txt"
    with open(vidgen_prompt_path, "r") as file:
        video_generator_prompt = file.read()

    return video_generator_prompt

#region Channels
def request_new_channel_input(name: str):
    print(f"\nChannel: {name} is not registered. Please provide some additional information...")
    focus = input(f"Enter the channel: {name}'s focus: > ")
    mission = input(f"Enter the channel: {name}'s mission: > ")

    channel = {
        "channel_name": name,
        "channel_focus": focus,
        "channel_mission": mission,
        "thread_id": None
    }

    return channel


def channel_name_is_registered(name: str) -> bool:
    print(f"\nChecking if Channel: {name} is registered...")
    channels = get_channels()
    result = False
    for channel in channels:
        if channel["channel_name"] == name:
            result = True
            break
    print(f"\tChannel: {name} Registered: {result}.")
    return result



def get_channels():
    print("\nLoading channels.yaml...")
    channels_path = "appdata/prompts/gpt/channels.yaml"
    with open(channels_path, "r") as file:
        config_dict = yaml.safe_load(file)
    print("\tChannels Loaded.")
    return config_dict.get("channels", [])



def get_channel(channel_name):
    channels = get_channels()
    for channel in channels:
        if channel["channel_name"] == channel_name:
            return channel
    return None


def save_channels(channels_data):
    channels_path = "appdata/prompts/gpt/channels.yaml"
    with open(channels_path, "w") as file:
        yaml.safe_dump(channels_data, file, default_flow_style=False, sort_keys=False, indent=2, width=80)

def register_channel(new_channel):
    print(f"\nRegistering New Channel: {new_channel['channel_name']}")
    channels_data = {"channels": get_channels()}
    channels_data["channels"].append(new_channel)
    save_channels(channels_data)
    print(f"\tChannel: {new_channel['channel_name']} Registered.")

def update_channel(updated_channel):
    print(f"\nUpdating Channel: {updated_channel['channel_name']}")
    channels_data = {"channels": get_channels()}
    for idx, channel in enumerate(channels_data["channels"]):
        if channel["channel_name"] == updated_channel["channel_name"]:
            channels_data["channels"][idx] = updated_channel
            break
    save_channels(channels_data)
    print(f"\tChannel: {updated_channel['channel_name']} Updated.")


def check_and_register_channel(channel_name):
    if not channel_name_is_registered(channel_name):
        channel = request_new_channel_input(channel_name)
        register_channel(channel)
#endregion


# Gets a video idea from the VidGen Assistant (making the assistant and registering channels as needed)

def query_vidgen_assistant(chat: ChatGPT, channel_name, source_material):
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
        update_channel(channel)
    else:
        thread = chat.get_thread_by_id(channel["thread_id"])

    chat.generate_user_message(source_material, thread)

    channel_instructions = yaml.dump(get_channel(channel_name), default_flow_style=False, sort_keys=False, indent=2, width=80)

    result = chat.run_assistant_thread(thread, vidgen_prompt_assistant, channel_instructions)
    json_results = Helper.convert_string_to_json(result)
    filesafe_filename = Helper.make_string_filesafe(json_results["Title"])
    filesafe_dirname = Helper.make_string_filesafe(channel_name)
    file_path = f"{ROOT_OUTPUT_DIR}/{filesafe_dirname}/{filesafe_filename}"
    Helper.save_json_to_file(json_results, file_path)
    return json_results




def main():
    # Ensure channels have proper output file structure
    for channel in get_channels():
        dir_name = Helper.make_string_filesafe(channel["channel_name"])
        Helper.create_directory_structure(f"{ROOT_OUTPUT_DIR}/{dir_name}")

    chat = ChatGPT()
    source_material = Helper.get_web_page("https://thespacereview.com/article/4808/1")
    # print(source_material)
    video_idea = query_vidgen_assistant(chat, "SpaceSecrets", source_material)




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


if __name__ == '__main__':
    main()
