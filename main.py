#!env/bin/python

from common.browser import WebBrowser
from common.youtube import YoutubeUploader, YoutubeArgs
from common.visla import Visla
from time import sleep

def main():
    # visla = Visla()
    # visla.log_on()
    # visla.create_video()
    # visla.download_video()

    youtube = YoutubeUploader(YoutubeArgs("/home/neon/Videos/OBS/2024-05-13 04-34-44.mp4",
                             "Hello World2",
                             "test video",
                             22,
                             "test, hello world",
                             "private"))
    youtube.run()


if __name__ == '__main__':
    main()
