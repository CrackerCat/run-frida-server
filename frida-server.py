#! /usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Jonas "6a6f6a6f" Uliana'
__copyright__ = "Copyright 2022, Hackerspace 016"

import json
import lzma
import sys
import tempfile
from os import remove

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

    exit_code, _, _ = run_adb_command('shell su -c "id"')
    if exit_code != 0:
        print(f'{err} Your device {bold("must be rooted")}!')
        exit(1)

    _, pid, _ = run_adb_command('shell su -c "pgrep frida-server"')
    if pid:
        print(f'{err} You already have a process named {bold("frida-server")} running!')
        exit(1)

    _, arch, _ = run_adb_command('shell getprop ro.product.cpu.abi')
    if not arch:
        print(f'{err} Unable to verify what ABI your Android is based!')
        exit(1)

    # TODO:
    # - Improve ABI detection
    if arch == 'x86':
        frida_abi = 'x86'
    elif 'arm64' in arch:
        frida_abi = 'arm64'
    else:
        frida_abi = 'x86_64'

    remote = ''
    assets = get('https://api.github.com/repos/frida/frida/releases/latest').json()['assets']
    for asset in assets:
        name = str(asset['name'])
        if name.startswith('frida-server') and 'android' in name and frida_abi in name:
            remote = asset['browser_download_url']

    if not remote:
        print(f'{err} Unable to found a suitable frida-server for your ABI!')
        print(f'{warn} Please, open a issue with this value: "{frida_abi}:{arch}".')
        exit(1)

    print(f'{info} Downloading latest frida-server for {arch}...')
    file = tempfile.NamedTemporaryFile()
    response = get(remote)
    file.write(response.content)

    with lzma.open(file.name) as f1:  # 👀 rs
        buffer = f1.read()
        with open('frida-server', 'wb') as f2:
            f2.write(buffer)
    file.close()
    run_adb_command('push ./frida-server /data/local/tmp')
    remove('frida-server')
    print(f'{info} Starting frida-server...')
    run_adb_command('shell su -c "chmod +x /data/local/tmp/frida-server"')
    run_adb_command('shell su -c "/data/local/tmp/frida-server -D"', True)
    print(f'{info} frida-server {bold("running and up")}!')


if __name__ == '__main__':
    main()
