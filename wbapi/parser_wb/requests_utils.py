from typing import Optional
import os

import requests

def download_pic(pic_url: str, data_folder: Optional[str] = None, name: Optional[str] = None) -> Optional[bytes]:
    data = requests.get(pic_url).content
    if data_folder:
        if not name:
            raise Exception('Name for saving is required!')
        with open(os.path.join(data_folder, f'{name}.jpg'), 'wb') as f:
            f.write(data)
    else:
        return data
