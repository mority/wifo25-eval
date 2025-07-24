import json

r = []

with open("responses.txt") as f:
    for l in f:
        r.append(json.loads(l))

for i in r:
    print(i["debugOutput"])