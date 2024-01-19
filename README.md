# KappaSigmaMu Bot

Element bot for Kusama Society V2

### Managing Proof-of-Ink images

We use IPFS to host the images and Pinata to pin the folder. The images are optimized and renamed to `<member_hash>.jpg` before getting uploaded. The scripts can be found inside `scripts/poi`.

#### Requirements:
- Python libraries:
```
pip3 install Pillow pillow-heif python-dotenv
```

#### Optimizing images
- Optimize an entire folder:
```
python3 optimize_multiple.py <folder_path>
```
- Rename and optimize single image:
```
python3 rename_and_optimize.py <image_path> <member_hash>
```

#### Interacting with IPFS/Pinata
- PS: requires a `.env` inside `scripts/poi` with `PINATA_API_KEY` and `PINATA_API_SECRET`
- Install IPFS and run it:
```
ipfs daemon
```
- Upload folder to Pinata and pin it:
```
python3 upload.py <file_path>
```
- Download pinned folder:
```
python3 download.py <ipfs_hash> <download_path>
```
- Full job - takes a new image, renames and optimizes it, uploads the new folder to Pinata and pins it, and finally unpins the old folder. The optional param `force` let's you overwrite an image that already exists.
```
python3 job.py <image_path> <member_hash> [optional=force]
```
