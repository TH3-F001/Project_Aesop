#!env/bin/python

from common.browser import WebBrowser
from common.youtube import YoutubeUploader, YoutubeArgs
from common.chatgpt import ChatGPT
from common.visla import Visla
from time import sleep

def main():
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

    chat = ChatGPT()
    chat.request_video_prompt()

if __name__ == '__main__':
    main()
