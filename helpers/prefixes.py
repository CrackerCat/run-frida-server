#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from termcolor import colored

info = colored('i', color='blue', attrs=['bold'])
err = colored('e', color='red', attrs=['bold'])
warn = colored('w', color='yellow', attrs=['bold'])


def bold(text: str) -> str:
    return colored(text, attrs=["bold"])
