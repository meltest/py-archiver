#!/usr/bin/env python3
import os
import sys
from argparse import ArgumentParser
from dotenv import load_dotenv
from boxsdk import JWTAuth
from boxsdk import Client
from boxsdk import BoxAPIException

abs_dirpath = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(abs_dirpath, ".env")
load_dotenv(dotenv_path)

### Define box parameters here
BOX_FOLDER_ID = os.environ.get("BOX_FOLDER_ID")

def argument_parser():
    usage = 'python3 {} -f <file> -c <config>'.format(__file__)
    description = 'Upload or update file to Box'

    params = {}
    argparser = ArgumentParser(usage=usage, description=description)
    argparser.add_argument('-f', type=str, dest='target_file', help='Target fle. If file does not exist, upload it. If file exists, update content.', required=True)
    argparser.add_argument('-c', type=str, dest='config_file', help='Path to your config file. You must specify this option absolute path.', required=True)

    args = argparser.parse_args()
    if not os.path.exists(args.target_file):
        sys.exit('No such file found.')
    else:
        params['f'] = args.target_file

    if not os.path.exists(args.config_file):
        sys.exit('No such config file found.')
    else:
        params['c'] = args.config_file

    return params

def get_file_id(client, target_file_path):
    target_file = os.path.basename(target_file_path)
    folder_id = BOX_FOLDER_ID

    box_files = client.folder(folder_id).get_items()
    file_id = ''

    for item in box_files:
        if item.name == target_file:
            file_id = item.id
            break

    return file_id

def upload_file(client, target_file_path):
    file_size = os.path.getsize(target_file_path)
    file_size_mb = file_size / (1024 * 1024)

    folder_id = BOX_FOLDER_ID
    # when target file is over 50 MB use chunked upload
    if file_size_mb > 50:
        try:
            print(f'File size is over 50MB. Using chunked upload...')
            chunked_uploader = client.folder(folder_id).get_chunked_uploader(target_file_path)
            uploaded_file = chunked_uploader.start()
            print(f'File "{uploaded_file.name}" uploaded to Box with file ID {uploaded_file.id}')
        except BoxAPIException as e:
            print(f"Got an error. Status: {e.status}, Context: {e.context_info}.")
            sys.exit()
    # ohterwise, use normal upload
    else:
        try:
            new_file = client.folder(folder_id).upload(target_file_path)
            print(f'File "{new_file.name}" uploaded to Box with file ID {new_file.id}')
        except BoxAPIException as e:
            print(f"Got an error. Status: {e.status}, Context: {e.context_info}.")
            sys.exit()

def update_file(client, target_file_path, file_id):
    file_size = os.path.getsize(target_file_path)
    file_size_mb = file_size / (1024 * 1024)

    # when target file is over 50 MB use chunked upload
    if file_size_mb > 50:
        try:
            print(f'File size is over 50MB. Using chunked upload...')
            chunked_uploader = client.file(file_id).get_chunked_uploader(target_file_path)
            uploaded_file = chunked_uploader.start()
            print(f'File "{uploaded_file.name}" uploaded to Box with file ID {uploaded_file.id}')
        except BoxAPIException as e:
            print(f"Got an error. Status: {e.status}, Context: {e.context_info}.")
            sys.exit()
    # ohterwise, use normal upload
    else:
        try:
            updated_file = client.file(file_id).update_contents(target_file_path)
            print(f'File "{updated_file.name}" has been updated')
        except BoxAPIException as e:
            print(f"Got an error. Status: {e.status}, Context: {e.context_info}.")
            sys.exit()

def main():
    params = argument_parser()
    target_file_path = params['f']
    config_file_path = params['c']
    print(f'target file is {target_file_path}')

    auth = JWTAuth.from_settings_file(config_file_path)
    client = Client(auth)

    # get file id
    file_id = get_file_id(client, target_file_path)

    # when file doesn't exist
    if not file_id:
        print(f'{target_file_path} does not exist. uploading as new file...')
        upload_file(client, target_file_path)
    # when file exists
    else:
        print(f'{target_file_path} exists. uploading as new version...')
        update_file(client, target_file_path, file_id)

if __name__ == "__main__":
    main()
