from typing import List, Union
from contextlib import contextmanager

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
    def create_wb_api(api_key: str) -> None:
        wb_api = WbApi(api_key)
        yield wb_api
        wb_api._close()

    def get_vendors(self, limit: int = -1) -> List[str]:
        send_json = {
            'sort': {
                'cursor': {
                    'limit': 1000 if limit == -1 else limit
                },
                'filter': {
                    'withPhoto': -1
                }
            }
        }

        all_json = self.session.post(
            self.url + '/content/v1/cards/cursor/list',
            json=send_json
        ).json()
        all_vendors = [card['vendorCode'] for card in all_json['data']['cards']]
        return all_vendors

    def get_cards_by_vendors(self, vendors: Union[List[str], str]) -> list:
        if isinstance(vendors, str):
            vendors = [vendors]

        send_json = {'vendorCodes': vendors}

        all_json = self.session.post(
            self.url + '/content/v1/cards/filter',
            json=send_json
        ).json()
        return all_json['data']

    def analyze_cards(self, cards: list) -> list:
        cards_empty = []
        for card in tqdm(cards, desc='Analyzing cards'):
            char = set(map(lambda x: tuple(x.keys())[0], card['characteristics']))
            print(char)
            if not ('Длина упаковки' in char and 'Высота упаковки' in char and 'Ширина упаковки' in char):
                cards_empty.append(card)

        print(f'Всего найдено артикулов без габаритов - {len(cards_empty)}')
        return cards_empty

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

        print(cards_modify)

        r = self.session.post(
            self.url + '/content/v1/cards/update',
            json=cards_modify
        )

        return r.status_code == 200

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

    def _close(self):
        self.session.close()
