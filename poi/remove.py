import os
import requests
import sys
import traceback
from datetime import datetime
from dotenv import load_dotenv
from poi.download import download
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


def remove_file_from_folder(image_folder, member_hash):
    file_name = f"{member_hash}.jpg"
    file_path = os.path.join(
        image_folder, os.path.basename(file_name))

    if not os.path.exists(file_path):
        message = f"Image for this address does not exist."
        print(message)
        sys.exit(message)

    os.remove(file_path)
    print(f"File {file_name} removed")


def remove(member_hash):
    try:
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        image_folder = f"poi/images-{timestamp}"

        current_pinned_hash = get_latest_pinned_hash()
        download(current_pinned_hash, image_folder)

        remove_file_from_folder(image_folder, member_hash)

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
    if len(sys.argv) != 2:
        print("Usage: python3 remove.py <member_hash>")
        sys.exit(1)

    member_hash = sys.argv[1]
    remove(member_hash)


if __name__ == "__main__":
    main()
