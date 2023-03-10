import os
import pickle

from tqdm import tqdm

from wbapi.api import WbApi

cards_to_modify = []
for file_name in os.listdir('data/cards_empty_dop_1/'):
    with open(f'data/cards_empty_dop_1/{file_name}', 'rb') as f:
        cards_to_modify.extend(list(pickle.load(f)))

with WbApi.create_wb_api() as wb_api:
    for i in tqdm(range(100000, len(cards_to_modify), 100)):
        wb_api.change_cards(cards_to_modify[i:i + 100])

