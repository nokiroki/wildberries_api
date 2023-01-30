import os
import argparse
from configparser import ConfigParser
import pickle

import pandas as pd

from tqdm import tqdm

from api import WbApi


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='api information')

    parser.add_argument('-t', '--token', dest='api_key', help='api token')
    parser.add_argument('-m', '--mode', dest='mode', help='launch mode', default='modify')

    return parser.parse_args()

def modify_cards(wb_api: WbApi, vendor_list: list, save_dir: str) -> None:
    wb_api.raw_save(vendor_list, save_dir)
    all_vendors = []
    for filename in os.listdir(save_dir):
        with open(os.path.join(save_dir, filename), 'rb') as f:
            data = pickle.load(f)
            all_vendors.extend(data)
    print(f'Всего артикулов - {len(all_vendors)}')
    for i in tqdm(range(0, len(all_vendors), 100)):
        code = wb_api.change_cards(all_vendors[i : i + 100], True)
        if not code:
            print('Warning')

def update_sizes(wb_api: WbApi, save_dir: str) -> None:
    all_vendors = []
    for filename in os.listdir(save_dir):
        with open(os.path.join(save_dir, filename), 'rb') as f:
            data = pickle.load(f)
            all_vendors.extend(data)
    print(f'Всего артикулов - {len(all_vendors)}')
    _, _, cards_to_modify = wb_api.analyze_cards(all_vendors)
    print(f'Нужно поменять - {len(cards_to_modify)}')
    for i in tqdm(range(0, len(cards_to_modify), 100)):
        code = wb_api.update_sizes(cards_to_modify[i : i + 100])
        if not code:
            print('Warning')

def save_table_with_cards(wb_api: WbApi, vendor_file: str, column_name: str, save_dir: str) -> None:
    ext = vendor_file.split('.')[1]
    if ext == 'xlsx':
        vendors = pd.read_excel(vendor_file)[column_name].tolist()
    else:
        vendors = pd.read_csv(vendor_file)[column_name].tolist()
    wb_api.get_chars(vendors, save_dir)

if __name__ == '__main__':
    config = ConfigParser()
    config.read('config.ini', encoding='utf-8')

    args = parse_args()
    if not args.api_key:
        if config['Wb_api']['token']:
            api_token = config['Wb_api']['token']
        else:
            raise Exception('Api token is required!')
    else:
        api_token = args.api_key

    main_folder = config['Data']['main_data_folder']
    vendor_file_name = os.path.join(main_folder, config['Data']['vendor_file'])
    saving_dir = os.path.join(main_folder, config['Data']['save_folder'])
    with WbApi.create_wb_api(api_token) as wb_api:
        vendors = pd.read_excel('data/new_vendors.xlsx')['Артикул продавца'].values.tolist()
        modify_cards(wb_api, vendors, 'data/new_data')
        # save_table_with_cards(wb_api, vendor_file_name, config['Vendor_list']['vendor_name'], saving_dir)
