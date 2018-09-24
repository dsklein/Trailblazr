import io
import json
import sys
import time

from coord_tools import get_elevation

if len(sys.argv) != 3:
	print('Wrong number of arguments! Exiting.')

infile_name = sys.argv[1]
outfile_name = sys.argv[2]

# Declare dict to hold coordinates
node_coords = {}
fail_count = 0
nodes_processed = 0

# Read in each node from a file
infile = open(infile_name,'r')
for line in infile.readlines():
	fields = line.split()
	node_id = int(fields[0])
	lat = float(fields[1])
	lon = float(fields[2])

	elev = get_elevation(lat,lon)
	if elev < 0:
		print('Warning: bad elevation result')
		fail_count += 1
	else:
		fail_count = 0

	node_coords[node_id] = [lat,lon,elev]
	nodes_processed += 1
	if nodes_processed % 1000 == 0:
		print(f'Processed {nodes_processed} nodes so far...')
		time.sleep(10)
	if fail_count > 100:
		print('Aborting due to 100 consecutive failures')
		break
	#time.sleep(.5)

infile.close()

# Print the 3-coord nodes to the outfile
with open(outfile_name,'w') as outfile:
	json.dump(node_coords,outfile)

print(f'Wrote {nodes_processed} nodes to file {outfile_name}.')
