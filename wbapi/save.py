import pandas as pd

from .api import WbApi

def save_table_with_cards(wb_api: WbApi,
                          vendor_file: str,
                          column_name: str,
                          save_dir: str,
                          save_every: int) -> None:
    ext = vendor_file.split('.')[1]
    if ext == 'xlsx':
        vendors = pd.read_excel(vendor_file)[column_name].tolist()
    else:
        vendors = pd.read_csv(vendor_file)[column_name].tolist()
    wb_api.get_chars(vendors, save_dir, save_every=save_every)
