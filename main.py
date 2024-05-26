#!env/bin/python

from common.browser import WebBrowser
from common.visla import Visla
from time import sleep

def main():
    visla = Visla()
    visla.log_on()


if __name__ == '__main__':
    main()
