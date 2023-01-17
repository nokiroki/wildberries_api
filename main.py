import os
import argparse
from configparser import ConfigParser

import pandas as pd

from tqdm import tqdm

from api import WbApi


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='api information')

    parser.add_argument('-t', '--token', dest='api_key', help='api token')

    return parser.parse_args()


if __name__ == '__main__':
    config = ConfigParser()
    config.read('config.ini')

    args = parse_args()
    if not args.api_key:
        if config['Wb_api']['token']:
            api_token = config['Wb_api']['token']
        else:
            raise Exception('Api token is required!')
    else:
        api_token = args.api_key

    with WbApi.create_wb_api(api_token) as wb_api:
        wb_api.get_chars(['ZMS-021'])
