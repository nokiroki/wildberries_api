import os
import pickle
from time import sleep, time

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

def modify_sizes(
    wb_api: WbApi,
    vendor_file: str,
    sleep_between: int = 0,
    limit_in_minute: int = -1
) -> None:
    vendor_list = pd.read_excel(vendor_file)
    vendor_list = vendor_list.values.T
    vendors_id = vendor_list[0].tolist()
    sizes = vendor_list[1:].T.tolist()

    start_time = time()
    time_delta = 0
    for i in tqdm(range(0, len(vendors_id), 100)):
        vendors_keys = dict(zip(vendors_id[i : i + 100], sizes[i : i + 100]))
        wb_api.change_sizes(
            wb_api.get_cards_by_vendors(vendors_id[i : i + 100]),
            vendors_keys
        )

        sleep(sleep_between)
        time_delta += time() - start_time
        if limit_in_minute > 0 and (i + 1) % limit_in_minute == 0:
            if time_delta < limit_in_minute:
                sleep(limit_in_minute - time_delta)
            time_delta = 0
            start_time = time()

def modify_vendors(wb_api: WbApi, vendor_file: str) -> None:
    vendor_list = pd.read_excel(vendor_file)
    vendor_list = vendor_list.values.T
    vendors_id = vendor_list[0].tolist()
    vendors_new = vendor_list[1].tolist()

    for i in tqdm(range(0, len(vendors_id), 100)):
        vendors_keys = dict(zip(vendors_id[i : i + 100], vendors_new[i : i + 100]))
        wb_api.change_suppliers_vendors(
            wb_api.get_cards_by_vendors(vendors_id[i : i + 100]),
            vendors_keys
        )

def modify_name_description(wb_api: WbApi, vendor_file: str) -> None:
    nd_list = pd.read_excel(vendor_file)
    nd_list = nd_list.values.T
    vendors = nd_list[0].tolist()
    name_description = nd_list[1:].T.tolist()
    if len(name_description[0]) == 1:
        name_description = list(map(lambda x: (x, None), name_description))

    for i in tqdm(range(0, len(vendors), 100)):
        vendors_keys = dict(zip(vendors[i : i + 100], name_description[i : i + 100]))

        wb_api.change_name_description(
            wb_api.get_cards_by_vendors(vendors[i : i + 100]),
            vendors_keys
        )
