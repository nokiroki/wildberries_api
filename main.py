import os
from typing import Sequence, Optional
import argparse
import pickle

import pandas as pd

from tqdm import tqdm

from api import WbApi


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='api information')

    parser.add_argument('api_key', type=str, help='api token')

    return parser.parse_args()


def load_and_save(api_token: str) -> None:
    with WbApi.create_wb_api(api_token) as wb_api:
        data = wb_api.get_cards_by_vendors('MT2B-828470')
        print(data)
        with open('data\\vendors.pck', 'rb') as f:
            all_vendors = list(pickle.load(f))

        all_info, cards_empty = [], []
        errors_list = []
        for i in tqdm(range(0, len(all_vendors), 50)):
            data = wb_api.get_cards_by_vendors(all_vendors[i:i + 50])
            print(f'Полученно карточек - {len(data)}')
            all_info_100, cards_empty_100 = wb_api.analyze_cards(data)
            all_info.extend(all_info_100)
            cards_empty.extend(cards_empty_100)

            if i % 500 == 0:
                print('Saving...')
                with open(f'data\\all_info\\all_data_part_{i // 500}.pcl', 'wb') as f_info:
                    with open(f'data\\cards_empty\\cards_empty_part_{i // 500}.pcl', 'wb') as f_empty:
                        pickle.dump(all_info, f_info)
                        pickle.dump(cards_empty, f_empty)
                all_info.clear()
                cards_empty.clear()

        print('Saving...')
        with open(f'data\\all_info\\all_data_part_{len(all_vendors) // 500 + 1}.pcl', 'wb') as f_info:
            with open(f'data\\cards_empty\\cards_empty_part_{len(all_vendors) // 500 + 1}.pcl', 'wb') as f_empty:
                pickle.dump(all_info, f_info)
                pickle.dump(cards_empty, f_empty)
        all_info.clear()
        cards_empty.clear()


def load_with_photo(api_token: str):
    with WbApi.create_wb_api(api_token) as wb_api:
        with open('data\\vendors.pck', 'rb') as f:
            all_vendors = list(pickle.load(f))

        for i in tqdm(range(0, len(all_vendors), 50)):
            data = wb_api.get_cards_by_vendors(all_vendors[i:i + 50])
            print(f'Полученно карточек - {len(data)}')
            wb_api.change_cards2(data, './data/default.jpg')


if __name__ == '__main__':
    args = parse_args()
    API_TOKEN = args.api_key
    load_with_photo(API_TOKEN)
    with WbApi.create_wb_api(API_TOKEN) as wb_api:
        data = wb_api.get_cards_by_vendors('MT2B-828470')
        print(data)
