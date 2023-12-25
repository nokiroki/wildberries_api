from typing import Optional
import os
import io
from time import time, sleep

import requests

import pandas as pd

from PIL import Image

from wbapi import WbApi
from utils.image_utils import resize_image


def upload_photos(
    wb_api: WbApi,
    vendor_file: str,
    is_global_path: bool = True,
    images_folder: Optional[str] = None,
    default_image_file: str = 'default.jpg'
) -> None:
    ext = vendor_file.split('.')[1]
    if ext == 'xlsx':
        df = pd.read_excel(vendor_file)
    else:
        df = pd.read_csv(vendor_file)

    start_time = time()
    time_delta = 0
    for i, vendor, image_file in enumerate(df.iloc):
        wb_api.delete_photos(vendor)
        image = Image.open(
            image_file if is_global_path else os.path.join(images_folder, image_file)
        )
        image = image.convert('RGB')
        resized_image = resize_image(image)
        if resized_image is not None:
            image_reader = io.BytesIO()
            resized_image.save(image_reader, 'jpeg')
            wb_api.upload_photo(vendor, image_reader)
        else:
            wb_api.upload_photo(vendor, os.path.join(images_folder, default_image_file))
        time_delta += time() - start_time
        if (i + 1) % 60 == 0:
            if time_delta < 60:
                sleep(60 - time_delta)
            time_delta = 0
            start_time = time()

def upload_cards(
    wb_api: WbApi,
    vendor_file: str
):
    ext = vendor_file.split('.')[1]
    df = pd.read_excel(vendor_file) if ext == "xlsx" else pd.read_csv(vendor_file)
    links_images = None
    if "image" in df:
        links_images = df["image"].values

    wb_api.upload_cards(df)
    if "image" in df:
        for vendor, image_link in zip(df["vendorCode"].values, links_images):
            image_stream = io.BytesIO(requests.get(image_link).content)
            wb_api.upload_photo(vendor, image_stream)
