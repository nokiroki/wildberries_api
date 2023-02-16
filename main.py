import os
import argparse
from configparser import ConfigParser

from wbapi import WbApi, save_table_with_cards, modify_cards, save_prices


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='api information')

    parser.add_argument('-t', '--token', dest='api_key', help='api token')
    parser.add_argument(
        '-m',
        '--mode',
        choices=('save', 'modify', 'get_prices'),
        dest='mode',
        help='launch mode',
        default='save'
    )
    parser.add_argument(
        '-d',
        dest='make_default_sizes',
        action='store_false',
        help='If present, program will not change existing sizes (in "modify" mode)'
    )

    return parser.parse_args()


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

    if not os.path.exists(saving_dir):
        os.mkdir(saving_dir)

    with WbApi.create_wb_api(api_token) as wb_api:
        if args.mode == 'save':
            save_table_with_cards(
                wb_api,
                vendor_file_name,
                config['Vendor_list']['vendor_name'],
                saving_dir,
                int(config['Saving']['save_every'])
            )
        elif args.mode == 'modify':
            modify_cards(
                wb_api,
                vendor_file_name,
                config['Vendor_list']['vendor_name'],
                saving_dir,
                args.make_default_sizes
            )
        elif args.mode == 'get_prices':
            save_prices(wb_api, saving_dir)
