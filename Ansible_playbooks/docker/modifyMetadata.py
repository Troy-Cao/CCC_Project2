import json
import argparse



parser = argparse.ArgumentParser()
parser.add_argument('-i', required=True, help="please enter an input file")
parser.add_argument('-o', required=True, help="please enter an output file name")
parser.add_argument('-n', required=True, help="please enter the new node's name")
args = parser.parse_args()


#newnode = "couchdb@172.26.131.195"
input = vars(args)['i']
output = vars(args)['o']
newnode = vars(args)['n']

with open(input) as json_file:
    data = json.load(json_file)

shards = []
for shard in data["by_range"]:
    shards.append(shard)
    if newnode not in data["by_range"][shard]:
        data["by_range"][shard].append(newnode)

data["by_node"][newnode] = []

for shard in shards:
    if ["add",shard, newnode] not in data["changelog"]:
        data["changelog"].append(["add",shard, newnode])
    if shard not in data["by_node"][newnode]:
        data["by_node"][newnode].append(shard)

with open(output, 'w') as outfile:
    json.dump(data, outfile)
