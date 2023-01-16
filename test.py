import os
import pickle

from tqdm import tqdm

from api import WbApi

cards_to_modify = []
for file_name in os.listdir('data/cards_empty_dop_1/'):
    with open(f'data/cards_empty_dop_1/{file_name}', 'rb') as f:
        cards_to_modify.extend(list(pickle.load(f)))

with WbApi.create_wb_api('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3NJRCI6IjA0MGEwYWQ0LWZiOGEtNGIwYS04NTM0LTQ5ZDUyYWJiOTlkYSJ9.rUoHKDBTQARX2t-M5gX87M5zY9kDBuJaFJmJfxfCtoA') as wb_api:
    for i in tqdm(range(100000, len(cards_to_modify), 100)):
        wb_api.change_cards(cards_to_modify[i:i + 100])

