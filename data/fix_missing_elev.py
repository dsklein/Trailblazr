import io,json,sys
from coord_tools import get_elevation


if len(sys.argv) != 3:
	print('Wrong number of arguments!')
	exit()

infilename = sys.argv[1]
outfilename = sys.argv[2]

with open(infilename,'r') as infile:
	data = json.load(infile)

print(f'Loaded {len(data.keys())} nodes.')

for node_id in data.keys():
	if data[node_id][2] < 0:
		lat,lon,elev = data[node_id]
		print(f'Attempting to fix elevation for node {node_id} ({lat},{lon})')
		data[node_id][2] = get_elevation(lat,lon)

with open(outfilename,'w') as outfile:
	json.dump(data,outfile)
print('Wrote data to '+outfilename)
		
