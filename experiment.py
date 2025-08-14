import argparse
import os.path
from tqdm import tqdm
import requests
import json
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument(
    "-u",
    "--url",
    help="the url of the MOTIS instance to send the queries to",
    type=str,
    default="http://localhost:6499",
)
parser.add_argument(
    "-q",
    "--queries",
    help="file containing queries to send to the MOTIS server",
    type=str,
    default="queries.txt",
)
parser.add_argument(
    "-r",
    "--responses",
    help="file to write the responses from the MOTIS server to ",
    type=str,
    default="responses.txt",
)
args = parser.parse_args()

if os.path.isfile(args.responses):
    print(args.responses + " already exists, quitting.")
    quit()

n_queries = 0
with open(args.queries, "r") as qf:
    for q in qf:
        n_queries += 1

with open(args.queries, "r") as qf, open(args.responses, "a") as rf:
    for q in tqdm(qf, total=n_queries):
        r = requests.get(args.url + q)
        rj = json.loads(r.text)
        for i in rj["itineraries"]:
            dep = pd.Timestamp(i["startTime"])
            arr = pd.Timestamp(i["endTime"])
            if dep > arr:
                print(
                    "\nquery:\n{}\nitinerary:\n{}\nresponse:\n{}".format(
                        q, json.dumps(i), json.dumps(rj)
                    )
                )
                quit()
        rf.write(r.text + "\n")
