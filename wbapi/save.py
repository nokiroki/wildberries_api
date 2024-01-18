import os

import pandas as pd

from .api import WbApi

def save_table_with_cards(
    wb_api: WbApi,
    vendor_file: str,
    column_name: str,
    save_dir: str,
    save_every: int,
    sleep_between: int = 0,
    limit_in_minute: int = -1
) -> None:
    ext = vendor_file.split('.')[1]
    if ext == 'xlsx':
        vendors = pd.read_excel(vendor_file)[column_name].tolist()
    else:
        vendors = pd.read_csv(vendor_file)[column_name].tolist()
    wb_api.get_chars(
        vendors,
        save_dir,
        save_every=save_every,
        sleep_between=sleep_between,
        limit_in_minute=limit_in_minute
    )


def save_prices(wb_api: WbApi, save_dir: str, save_every: int = 900000) -> None:
    prices = wb_api.get_prices()
    print(f'Total length - {len(prices)}')
    
    for i in range(0, len(prices), save_every):
        pd.DataFrame(prices[i:i + save_every]).to_excel(os.path.join(save_dir, f'data_{save_every}_{i // save_every}.xlsx'), index=False)
