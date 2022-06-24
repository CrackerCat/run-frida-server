#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from shutil import which
from subprocess import run, Popen
from time import sleep
from typing import IO

from termcolor import colored

from helpers.prefixes import err, info

signaler = ''
target_device = ''


def signaler_handler() -> any:
    max_tries = 6
    tries = 0
    while True:
        global signaler
        if not signaler:
            tries = tries + 1
            if tries == max_tries:
                print(
                    f'{err} Timeout when waiting for frida-server output, please, restart the script')
                exit(1)
            sleep(0.5)
        else:
            ret = signaler
            break
    signaler = ''
    return ret


def get_device() -> str:
    command_device = run(f'"{get_adb()}" devices',
                         capture_output=True, shell=True, universal_newlines=True)
    if command_device.returncode != 0:
        print(f'{err} Unable list available devices, check your ADB daemon!')
        exit(1)

    lines = command_device.stdout.strip().split('\n')
    devices = []
    device = ''
    del lines[0]
    for line in lines:
        if 'device' not in line:
            continue
        device = line.split()
        devices.append(device[0])

    if len(devices) == 0:
        print(f'{err} There is no available devices!')
        exit(1)

    if len(devices) > 1:
        print(
            f'{info} There is more than one device, which one you wanna use (select by the index)?')
        for i, device_name in enumerate(devices):
            new_index = i + 1
            print('-', f'[{new_index}]', device_name)

        user_choice = -1
        while user_choice == -1:
            try:
                user_choice = int(
                    input(colored('> ', color='yellow', attrs=['bold']))) - 1
                if user_choice < 0 or user_choice > len(devices) - 1:
                    print(f'{err} Your choice is out of range!')
                    user_choice = -1
                else:
                    device = devices[user_choice]
            except ValueError:
                print(f'{err} Your input must be a valid integer!')
    else:
        device = devices[0]

    global target_device
    target_device = device
    return device


def on_message(raw_message: dict, _):
    if raw_message:
        if 'payload' not in raw_message.keys():
            print(
                f'{err} frida-server answered something not expected, submit a issue!')
            print(
                f'This may help: "{colored(raw_message["description"], attrs=["bold"])}".')
            print(raw_message)
            exit(1)
        global signaler
        signaler = raw_message['payload']
        print(colored('f', color='grey', attrs=[
            'bold']), raw_message['payload'])


def get_adb() -> str:
    adb_path = which('adb')
    if adb_path is None:
        print(f'{err} Unable to find ADB in your PATH!')
        exit(1)

    return adb_path


def run_adb_command(command: str, background: bool = False) -> \
        tuple[int, IO[bytes] | None, IO[bytes] | None, int] | tuple[int, str, str]:
    if background:
        cmd = Popen([get_adb(), '-s', target_device] + command.split()) \
            if target_device else Popen([get_adb()] + command.split())
        return cmd.returncode, cmd.stdout, cmd.stderr, cmd.pid

    cmd = run(f'"{get_adb()}" -s {target_device} {command}', capture_output=True, shell=True, universal_newlines=True) \
        if target_device else run(f'{get_adb()} {command}', capture_output=True, shell=True, universal_newlines=True)
    return cmd.returncode, cmd.stdout.strip(), cmd.stderr.strip()
