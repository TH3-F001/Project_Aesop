#!env/bin/python

from common.browser import WebBrowser
from common.visla import Visla
from time import sleep

def main():
    visla = Visla()
    visla.open_homepage()
    sleep(2)
    visla.sign_in_for_first_time()


if __name__ == '__main__':
    main()
