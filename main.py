import os
import argparse
from configparser import ConfigParser

from wbapi import (
    WbApi,
    save_table_with_cards,
    modify_cards,
    save_prices,
    upload_photos
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='api information')

    parser.add_argument('-t', '--token', dest='api_key', help='api token')
    parser.add_argument(
        '-m',
        '--mode',
        choices=('save', 'modify', 'get_prices', 'upload_images'),
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
    parser.add_argument(
        '-g',
        '--global_path',
        dest='is_global_path',
        action='store_true',
        help='If present, program will consider images path name as their global name (in "upload_images" mode)'
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
    image_folder = os.path.join(main_folder, config['Data']['image_folder'])
    image_vendor_file_name = os.path.join(main_folder, config['Data']['image_vendor_file'])

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

        elif args.mode == 'upload_images':
            upload_photos(
                wb_api,
                image_vendor_file_name,
                args.is_global_path,
                image_folder
            )
