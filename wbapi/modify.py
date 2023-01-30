import os
import pickle

from tqdm import tqdm

import pandas as pd

from .api import WbApi

def modify_cards(
        wb_api: WbApi,
        vendor_file: str,
        column_name: str,
        save_dir: str,
        make_default_sizes: bool
) -> None:
    ext = vendor_file.split('.')[1]
    if ext == 'xlsx':
        vendor_list = pd.read_excel(vendor_file)[column_name].tolist()
    else:
        vendor_list = pd.read_csv(vendor_file)[column_name].tolist()

    wb_api.raw_save(vendor_list, save_dir)
    all_vendors = []
    for filename in os.listdir(save_dir):
        with open(os.path.join(save_dir, filename), 'rb') as f:
            data = pickle.load(f)
            all_vendors.extend(data)
    print(f'Всего артикулов - {len(all_vendors)}')
    for i in tqdm(range(0, len(all_vendors), 100)):
        code = wb_api.change_cards(all_vendors[i : i + 100], make_default_sizes)
        if not code:
            print('Warning')
