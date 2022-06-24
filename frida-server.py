#! /usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Jonas "6a6f6a6f" Uliana'
__copyright__ = "Copyright 2022, Hackerspace 016"

import lzma
import sys
import tempfile
from os import remove
from time import sleep

from colorama import init
from requests import get

from helpers.adb import get_device, run_adb_command
from helpers.prefixes import err, bold, info, warn


def main():
    init()

    if sys.platform != 'darwin' or sys.platform.startswith('linux'):
        print(f'{err} Your host device must be {bold("Linux or macOS")}!')
        print(f'{info} Try running under WSL2 case you are using Windows.')
        exit(1)

    device = get_device()
    print(f'{info} Using device {bold(device)} as the pwning host.')

    exit_code, _, _ = run_adb_command('shell su 0 id')
    if exit_code != 0:
        print(f'{err} Your device {bold("must be rooted")}!')
        exit(1)

    _, pid, _ = run_adb_command('shell su 0 pgrep frida-server')
    if not pid:
        print(f'{warn} frida-server {bold("is not running")}!')
        file = tempfile.NamedTemporaryFile()
        print(f'{info} Downloading frida-server for arm64...')
        response = get('https://github.com/frida/frida/releases/download/'
                       '15.1.27/frida-server-15.1.27-android-arm64.xz')
        file.write(response.content)

        with lzma.open(file.name) as f1:  # 👀 rs
            buffer = f1.read()
            with open('frida-server', 'wb') as f2:
                f2.write(buffer)
        file.close()
        run_adb_command('push ./frida-server /data/local/tmp')
        remove('frida-server')
        print(f'{info} Starting frida-server...')
        run_adb_command('shell su 0 chmod +x /data/local/tmp/frida-server')
        run_adb_command('shell su 0 /data/local/tmp/frida-server -D', True)
        print(f'{info} frida-server {bold("running and up")}!')


if __name__ == '__main__':
    main()
