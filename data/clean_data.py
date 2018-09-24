import io
import json
import sys


# First command-line argument is the file to open.
# If no file is specified, use the usa data as a default
filename = 'data_usa.json'
if len(sys.argv) == 2:
	filename = sys.argv[1]
elif len(sys.argv) > 2:
	print('Too many arguments specified! Exiting...')
	exit()

# Open the data file
with open(filename,'r') as infile:
	data = json.load(infile)

# Count the entries
num_elements = len(data['elements'])
print(f'Found {num_elements} elements.')
if num_elements == 0:
	print('Exiting...')
	exit()

num_nodes = 0
num_trails = 0
unique_nodes = set()

nodelist = []
nodelist_uniq = []
traillist = []

count = 0

#### Flag to enable debugging printout
debug = 0

# Loop over the entries
print('Running looper...')
for entry in data['elements']:
	
	# Examine the nodes
	if entry['type'] == 'node':
		num_nodes+=1
		blank_node = {}
		blank_node['id'] = entry['id']
		blank_node['lat'] = entry['lat']
		blank_node['lon'] = entry['lon']
		nodelist.append(blank_node)
	
	# Examine the ways (==pistes)
	elif entry['type'] == 'way':
		num_trails+=1

		if debug: print(f'Processing way {count}:',end='')
		count += 1
		
		# Filter out loop trails
		if entry['nodes'][0] == entry['nodes'][-1]:
			if debug: print('\tDiscarding loop trail.')
			continue

		blank_trail = {}
		difficulty = ''
		

		# Clean the difficulty tags
		if 'piste:difficulty' not in entry['tags']:
			if debug: print('\tDiscarding for no difficulty.')
			continue
		
		if entry['tags']['piste:difficulty'] == 'novice':
			difficulty = 'easy'
		elif entry['tags']['piste:difficulty'] == 'green':
			difficulty = 'easy'
		elif entry['tags']['piste:difficulty'] == 'difficult':
			difficulty = 'advanced'
		elif entry['tags']['piste:difficulty'] == 'Difficult':
			difficulty = 'advanced'
		elif entry['tags']['piste:difficulty'] == 'extreme':
			difficulty = 'expert'
		elif entry['tags']['piste:difficulty'] == 'medium':
			difficulty = 'intermediate'
		elif entry['tags']['piste:difficulty'] == 'Intermediate':
			difficulty = 'intermediate'
		elif entry['tags']['piste:difficulty'] not in ['easy','intermediate','advanced','expert']:
			if debug: print(f"\tDiscarding for difficulty {entry['tags']['piste:difficulty']}.")
			continue
		else:
			difficulty = entry['tags']['piste:difficulty']

		blank_trail['id'] = entry['id']
		blank_trail['nodes'] = entry['nodes']
		blank_trail['rating'] = difficulty
		if 'name' in entry['tags'].keys() and entry['tags']['name'] != '':
			blank_trail['name'] = entry['tags']['name']
		else:
			blank_trail['name'] = 'unknown_'+str(entry['id'])
		if debug: print('\tKeeping!')

		traillist.append(blank_trail)

		for node_id in entry['nodes']: unique_nodes.add(node_id)
	
	# Anything else
	else:
		print(f"Unknown entry type: {entry['type']}")

# Keep only nodes that are used in a trail
print('Removing unused nodes...')
for node in nodelist:
	if node['id'] in unique_nodes: nodelist_uniq.append(node)

# Save the data
print('Saving data to new files...')
dict_nodes = {'nodes':nodelist_uniq}
dict_trails = {'trails':traillist}

with open('data_nodes.json','w') as outfile_nodes:
	json.dump(dict_nodes,outfile_nodes)
with open('data_trails.json','w') as outfile_trails:
	json.dump(dict_trails,outfile_trails)
	
print(f'Kept {len(traillist)} trails and {len(nodelist_uniq)} nodes.')
