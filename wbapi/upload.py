from typing import Optional
import os
import io

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

    for vendor, image_file in df.iloc:
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
