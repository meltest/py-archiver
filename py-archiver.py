#!/usr/bin/env python3
import os
import sys
import shutil
import glob
import requests
import datetime
import monthdelta
from argparse import ArgumentParser
from dotenv import load_dotenv
from boxsdk import JWTAuth
from boxsdk import Client
from boxsdk import BoxAPIException
# from slack_sdk import WebClient
# from slack_sdk.errors import SlackApiError

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

# SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
# SLACK_CHANNEL = os.environ.get("SLACK_CHANNEL")
### Define box parameters here
BOX_FOLDER_ID = os.environ.get("BOX_FOLDER_ID")

# client = WebClient(token=SLACK_BOT_TOKEN)

def argument_parser():
    usage = 'python3 {} -m <month> -c <config>'.format(__file__)
    description = 'Archive and upload logs to Box'

    params = {}
    argparser = ArgumentParser(usage=usage, description=description)
    argparser.add_argument('-m', type=str, dest='target_month', help='Target month. You must specify this option like YYYY-MM')
    argparser.add_argument('-c', type=str, dest='config_file', help='Path to your config file. You must specify this option absolute path.', required=True)

    args = argparser.parse_args()
    if args.target_month:
        try:
            tmp_datetime = datetime.datetime.strptime(args.target_month, "%Y-%m")
            params['m'] = args.target_month
        except ValueError as e:
            sys.exit("You must specify -m option like YYYY-MM")
    else:
        # datetime.date() -> YYYY-MM-DD
        today = datetime.date.today()
        # str -> "YYYY-MM"
        last_month = (today - monthdelta.monthdelta(1)).strftime("%Y-%m")

        params['m'] = last_month
    if not os.path.exists(args.config_file):
        sys.exit('No such config file found.')
    else:
        params['c'] = args.config_file

    return params

def archive_files(dir_name):
    dir_path = os.path.join(os.path.dirname(__file__), dir_name)
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)

    # get target files
    file_pattern = f'{os.path.dirname(__file__)}/{dir_name}-*'
    archive_files = glob.glob(file_pattern)

    if not archive_files:
        sys.exit('No target files')
    else:
        print('archive files ==========')
        for item in archive_files:
            print(item)
        print('========================')

    # move target files
    for item in archive_files:
        shutil.move(item, dir_path)

    print(f'Target files have been moved to {dir_path}')

    # archive directory to .zip
    if not os.path.exists(f'{dir_path}.zip'):
        shutil.make_archive(dir_path, 'zip', os.path.dirname(__file__), dir_name)
        print(f'{dir_path}.zip is created. Archive done')
    else:
        sys.exit(f'Archive file "{dir_path}.zip" already exists')

    return f'{dir_path}.zip'

def upload_archive(target_archive, config_file):
    # targer_archive is absolute path to file
    # auth = JWTAuth.from_settings_file(f'{os.path.dirname(__file__)}/.config.json')
    auth = JWTAuth.from_settings_file(config_file)
    client = Client(auth)

    try: 
        folder_id = BOX_FOLDER_ID
        new_file = client.folder(folder_id).upload(target_archive)
        print(f'File "{new_file.name}" uploaded to Box with file ID {new_file.id}')

        # folder = client.folder(folder_id).get()
        # print(f'Folder "{folder.name}" has {folder.item_collection["total_count"]} items in it')
    except BoxAPIException as e:
        # print(f"Got an error: {e.response['error']}")
        print(f"Got an error: {e.status}")
        sys.exit()

params = argument_parser()
target_month = params['m']
config_file = params['c']
print(f'target_month is {target_month}')

target_archive = archive_files(target_month)
upload_archive(target_archive, config_file)
