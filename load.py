import json
import pandas as pd
from tqdm import tqdm


def load(file) -> pd.DataFrame:
    print("loading {}".format(file))

    n_lines = 0
    with open(file, "r") as f:
        for ln in f:
            n_lines += 1

    data = []
    with open(file, "r") as f:
        for l in tqdm(f, total=n_lines):
            data.append(json.loads(l))
    df = pd.json_normalize(data)

    return df
