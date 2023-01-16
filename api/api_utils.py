from typing import List, Union, Optional, Tuple
from collections.abc import Generator
from contextlib import contextmanager
import os
from sys import maxsize
import pickle
from time import sleep

import requests

from tqdm import tqdm


class WbApi:

    def __init__(self, api_key: str, url: str = 'https://suppliers-api.wildberries.ru') -> None:
        self.api_key = api_key

        self.session = requests.Session()
        self.session.headers.update({'Authorization': api_key})

        self.url = url

    @staticmethod
    @contextmanager
    def create_wb_api(api_key: str) -> Generator['WbApi', None, None]:
        wb_api = WbApi(api_key)
        yield wb_api
        wb_api._close()

    def get_error_list(self) -> list:
        return self.session.get(self.url + '/content/v1/cards/error/list').json()

    def get_vendors(self,
                    limit: int = -1,
                    additional_saving: bool = True,
                    save_dir: str = 'data',
                    save_every: int = 10000,
                    file_to_start: Optional[str] = None) -> List[str]:
        print('begin scrapping...\n')

        if limit == -1:
            limit = maxsize

        total_step_post = min(limit, 1000)
        total_step_get = total_step_post

        all_vendors = []
        total_len = 0

        send_json = {
            'sort': {
                'cursor': {
                    'limit': total_step_post
                },
                'filter': {
                    'withPhoto': -1
                }
            }
        }
        saving_counter = 0
        if file_to_start:
            with open(file_to_start, 'rb') as f:
                start_params = tuple(pickle.load(f))
                send_json['sort']['cursor']['updatedAt'] = start_params[0]
                send_json['sort']['cursor']['nmID'] = start_params[1]
                saving_counter = start_params[2]

        while total_step_get >= total_step_post and limit > 0:
            print(send_json)
            all_json = self.session.post(
                self.url + '/content/v1/cards/cursor/list',
                json=send_json
            ).json()
            cursor = all_json['data']['cursor']
            all_vendors.extend([card['vendorCode'] for card in all_json['data']['cards']])

            total_step_get = cursor['total']
            print(f'{total_step_get} vendors got')
            total_len += total_step_get
            print(f'Total len - {total_len}')
            limit -= total_step_get
            total_step_post = min(limit, 1000)

            send_json['sort']['cursor']['updatedAt'] = cursor['updatedAt']
            send_json['sort']['cursor']['nmID'] = cursor['nmID']
            send_json['sort']['cursor']['limit'] = total_step_post

            if additional_saving and len(all_vendors) % save_every == 0:
                if not os.path.exists(save_dir):
                    os.mkdir(save_dir)
                with open(os.path.join(save_dir, f'vendors_{len(all_vendors)}_{saving_counter}.pcl'), 'wb') as f:
                    pickle.dump(all_vendors, f)
                saving_counter += 1
                all_vendors.clear()
                with open(os.path.join(save_dir, 'params.pcl'), 'wb') as f:
                    pickle.dump(
                        (send_json['sort']['cursor']['updatedAt'], send_json['sort']['cursor']['nmID'], saving_counter),
                        f)

        if additional_saving:
            if not os.path.exists(save_dir):
                os.mkdir(save_dir)
            with open(os.path.join(save_dir, f'vendors_{len(all_vendors)}_{saving_counter}.pcl'), 'wb') as f:
                pickle.dump(all_vendors, f)
            saving_counter += 1
            all_vendors.clear()
            with open(os.path.join(save_dir, 'params.pcl'), 'wb') as f:
                pickle.dump(
                    (send_json['sort']['cursor']['updatedAt'], send_json['sort']['cursor']['nmID'], saving_counter),
                    f)

        return all_vendors

    def get_cards_by_vendors(self, vendors: Union[List[str], str]) -> list:
        if isinstance(vendors, str):
            vendors = [vendors]

        send_json = {'vendorCodes': vendors}

        while True:
            r = self.session.post(
                self.url + '/content/v1/cards/filter',
                json=send_json
            )
            status_code = r.status_code
            if status_code != 200:
                print(f'Ошибка. Код ответа - {status_code}. Повторный запрос...')
                sleep(5)
            else:
                break

        all_json = r.json()

        return all_json['data']

    def get_name_and_skus(self, card: dict) -> list:
        name = ''
        for char in card['characteristics']:
            if 'Наименование' in char:
                name = char['Наименование']
                break

        skus = card['sizes'][0]['skus'].copy()
        answer = [card['vendorCode'], name]
        answer.extend(skus)
        return answer

    def analyze_cards(self, cards: list) -> Tuple[list, list]:
        cards_empty = []
        all_info = []
        for card in tqdm(cards, desc='Analyzing cards'):
            all_info.append(self.get_name_and_skus(card))
            char = set(map(lambda x: tuple(x.keys())[0], card['characteristics']))
            if not ('Длина упаковки' in char and 'Высота упаковки' in char and 'Ширина упаковки' in char):
                cards_empty.append(card)
                continue
            is_vendor_cr = False
            for char in card['characteristics']:
                if 'Наименование' in char and len(char['Наименование']) > 60:
                    cards_empty.append(card)
                    continue
                if 'Артикул производителя' in char:
                    is_vendor_cr = True
            if not is_vendor_cr:
                cards_empty.append(card)
                continue

        print(f'Всего найдено артикулов без габаритов - {len(cards_empty)}')
        return all_info, cards_empty

    def change_cards(self, cards: list) -> bool:
        sizes = [
            {'Длина упаковки': 30},
            {'Ширина упаковки': 15},
            {'Высота упаковки': 10}
        ]
        cards_modify = cards.copy()
        for card in cards_modify:
            new_char = sizes.copy()
            new_char.extend(card['characteristics'])
            card['characteristics'] = new_char
            is_vendor_cr = False
            for char in card['characteristics']:
                if 'Наименование' in char and len(char['Наименование']) > 60:
                    char['Наименование'] = char['Наименование'][:58]
                if 'Артикул производителя' in char:
                    is_vendor_cr = True
            if not is_vendor_cr:
                card['characteristics'].append({'Артикул производителя': card['vendorCode']})

        r = self.session.post(
            self.url + '/content/v1/cards/update',
            json=cards_modify
        )

        return r.status_code == 200

    def change_cards2(self, cards: list, media: str) -> None:
        cards_modify = cards.copy()
        changed_cards = 0
        uploaded_photo = 0
        global_change = False
        for card in tqdm(cards_modify, desc='Analyzing and changing cards'):
            is_changed = False
            if len(card['mediaFiles']) == 0:
                self.upload_photo(card['vendorCode'], media)
                print('photo uploaded')
                uploaded_photo += 1
            for char in card['characteristics']:
                if 'Наименование' in char and char['Наименование'][-1] != '!':
                    for char_2 in card['characteristics']:
                        if 'Длина упаковки' in char_2 and int(char_2['Длина упаковки']) > 50:
                            char_2['Длина упаковки'] = 30
                            is_changed, global_change = True, True
                        if 'Ширина упаковки' in char_2 and int(char_2['Ширина упаковки']) > 30:
                            char_2['Ширина упаковки'] = 15
                            is_changed, global_change = True, True
                        if 'Высота упаковки' in char_2 and int(char_2['Высота упаковки']) > 20:
                            char_2['Высота упаковки'] = 10
                            is_changed, global_change = True, True
            if is_changed:
                changed_cards += 1

        if global_change:
            r = self.session.post(
                self.url + '/content/v1/cards/update',
                json=cards_modify
            )
        print(f'Кол-во изменённых артикулов - {changed_cards}')
        print(f'Кол-во загруженных фоток - {uploaded_photo}')


    def strip_cards(self, cards: list) -> bool:
        cards_modify = cards.copy()
        for card in cards_modify:
            for char in card['characteristics']:
                if 'Наименование' in char and len(char['Наименование']) > 60:
                    char['Наименование'] = char['Наименование'][:60]
        print(cards_modify)
        r = self.session.post(
            self.url + '/content/v1/cards/update',
            json=cards_modify
        )
        print(r.json())
        return r.status_code == 200

    def upload_photo(self, card_vendor: str, media: str) -> None:
        headers = {
            'X-Vendor-Code': card_vendor,
            'X-Photo-Number': '1'
        }
        files = {
            'uploadfile': open(media, 'rb')
        }
        req = self.session.post(
            self.url + '/content/v1/media/file',
            headers=headers,
            files=files
        )
        print(req.status_code)

    def _close(self):
        self.session.close()
