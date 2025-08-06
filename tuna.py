from load import load
from util import uses_taxi

import pandas as pd
from datetime import datetime

service_start = 4 * 60

# time until next arrival
def tuna(t, itineraries):
    arr_min = datetime.max
    for i in itineraries:
        dep = datetime.fromisoformat(i['startTime'])
        arr = datetime.fromisoformat(i['endTime'])
        if t <= dep and arr < arr_min:
            arr_min = arr
    return arr_min - t

def tunas(itineraries):
    ret = [0] * 1440
    for t in range(service_start, 1440):
        ret[t] = tuna(t,itineraries)
    return ret

df = load()
tuna = [0] * 1440
print(type(df.at[0, 'itineraries'][0]['startTime']))