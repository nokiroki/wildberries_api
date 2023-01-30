from typing import List, Tuple

import pandas as pd


def get_list_of_vendors(path_to_file: str) -> List[Tuple[str, str, str]]:
    data = pd.read_excel(path_to_file)
    return data.values.tolist()
