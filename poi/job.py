import os
import requests
import shutil
import sys
import traceback
from datetime import datetime
from dotenv import load_dotenv
from poi.download import download
from poi.rename_and_optimize import rename_and_optimize
from poi.upload import unpin, upload

load_dotenv()

API_KEY = os.getenv('PINATA_API_KEY')
API_SECRET = os.getenv('PINATA_API_SECRET')


def get_latest_pinned_hash():
    url = 'https://api.pinata.cloud/data/pinList'

    headers = {
        'pinata_api_key': API_KEY,
        'pinata_secret_api_key': API_SECRET
    }

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            pinned_items = response.json().get('rows', [])

            if not pinned_items:
                print("No pinned items found.")
                return None

            latest_item = max(
                pinned_items, key=lambda x: x.get('date_pinned', ''))

            print(f"Latest pinned item: {latest_item.get('ipfs_pin_hash')}")
            return latest_item.get('ipfs_pin_hash')
        else:
            print(f"Error fetching pinned items: {response.text}")
            return None

    except Exception as e:
        print(f"Exception occurred: {e}")
        return None


def move_file_to_folder(file_path, destination_folder, force):
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    destination_file_path = os.path.join(
        destination_folder, os.path.basename(file_path))

    if os.path.exists(destination_file_path) and not force:
        message = f"Image for this member already exists. Use `force` to overwrite."
        print(message)
        sys.exit(message)

    shutil.move(file_path, destination_file_path)

    print(f"File {file_path} moved to {destination_file_path}")


def job(image_path, member_hash, force):
    try:
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        image_folder = f"poi/images-{timestamp}"

        current_pinned_hash = get_latest_pinned_hash()
        download(current_pinned_hash, image_folder)

        new_filename = rename_and_optimize(image_path, member_hash)
        move_file_to_folder(new_filename, image_folder, force)

        success, new_pinned_hash = upload(image_folder)
        if success and new_pinned_hash != current_pinned_hash:
            return unpin(current_pinned_hash), None
        return success, None
    except Exception as e:
        tb = traceback.format_exc()
        print(f"An error occurred: {e}")
        print("Traceback details:")
        print(tb)
        return False, e
    except SystemExit as e:
        print(f"Caught SystemExit: {e}")
        return False, e

def main():
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print(
            "Usage: python3 job.py <image_path> <member_hash> [optional=force]")
        sys.exit(1)

    image_path = sys.argv[1]
    member_hash = sys.argv[2]
    force = False

    if len(sys.argv) == 4 and sys.argv[3] == 'force':
        force = True

    job(image_path, member_hash, force)


if __name__ == "__main__":
    main()
