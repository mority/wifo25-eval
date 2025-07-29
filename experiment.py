import os.path
import requests
from tqdm import tqdm

motis_url = 'http://localhost:6499'
qf_path = 'queries.txt'
rf_path = 'responses.txt'

if os.path.isfile(rf_path):
    print(rf_path + ' exists, quitting.')
    quit()

n_queries = 0
with open(qf_path, 'r') as qf:
    for l in qf:
        n_queries += 1

with open(qf_path, 'r') as qf, open(rf_path, 'a') as rf:
    for q in tqdm(qf, total=n_queries):
        r = requests.get(motis_url + q)
        rf.write(str(r.json()) + '\n')