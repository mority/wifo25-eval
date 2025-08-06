import json
import pandas as pd

def load():
    data = []

    with open("responses.txt") as f:
        for l in f:
            data.append(json.loads(l))

    df = pd.json_normalize(data)
    return df

