from typing import Sequence, Optional
import argparse

from api import WbApi


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='api information')

    parser.add_argument('api_key', type=str, help='api token')

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    API_TOKEN = args.api_key

    with WbApi.create_wb_api(API_TOKEN) as wb_api:
        # all_vendors = wb_api.get_vendors(10)
        # cards = wb_api.get_cards_by_vendors(all_vendors)
        # print(cards)
        # wb_api.analyze_cards(cards)

        data = wb_api.get_cards_by_vendors('FA1-FG0107')
        print(data)
        # print(wb_api.change_cards(data))
        # print(wb_api.get_cards_by_vendors('FA1-FG0107'))
