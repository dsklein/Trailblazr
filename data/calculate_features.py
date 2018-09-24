import io
import json
import math
import sys

from coord_tools import lle_to_xyz_local, coord_distance, slope, horiz_distance

with open('nodes.json','r') as nodefile:
	node_lookup = json.load(nodefile)

# What data structure goes here? Pandas dataframe? Something else?
# Check in scikit-learn.
#
# Construct whatever will hold our trail data
# Try a dict/json first...
data_processed = {}

with open('data_trails.json','r') as trailfile:
	trail_json = json.load(trailfile)

count = 0

for trail in trail_json['trails']:

	# Pull in the basic info about the trail
	trail_id = trail['id']
	trail_name = trail['name']
	trail_rating = trail['rating']

	# Pull in the coordinates of each node
	node_id_list = trail['nodes']
	node_coord_list = []
	for id in node_id_list:
		node_coord_list.append(node_lookup[str(id)])

	# Now do some calculation with the node coordinates
	num_nodes = len(node_coord_list)
	[firstlat,firstlon,firstelev] = node_coord_list[0]
	[lastlat,lastlon,lastelev] = node_coord_list[-1]
	# Make sure node list goes from high to low
	if firstelev < lastelev:
		[firstelev,lastelev] = [lastelev,firstelev]
		node_coord_list.reverse()

	horiz_length = 0.
	steepest_slope = 999. # Technically, all our slopes will be negative
	flattest_slope = -999.
	max_up_slope = -999.
	north_south_asymmetry = -999
	# Loop through node pairs and calculate various quantities
	# Always go from highest node to lowest node, regardless of storage order

	for i in range(0,num_nodes-1):
		[lat1,lon1,elev1] = node_coord_list[i]
		[lat2,lon2,elev2] = node_coord_list[i+1]
		if [lat1,lon1] == [lat2,lon2]: continue # Avoid duplicate nodes
		[x1,y1,z1] = lle_to_xyz_local(lat1,lon1,elev1,firstlat,firstlon)
		[x2,y2,z2] = lle_to_xyz_local(lat2,lon2,elev2,firstlat,firstlon)
		rise = z2-z1
		run = math.sqrt( (x1-x2)**2 + (y1-y2)**2 )
		# if run==0:
		# 	print('Run == 0!')
		# 	print(f'Reference point: {firstlat},{firstlon}')
		# 	print(f'Node {node_id_list[i]}: x,y,z = {x1},{y1},{z1}.')
		# 	print(f'\tlat,lon,elev = {lat1},{lon1},{elev1}.')
		# 	print(f'Node {node_id_list[i+1]}: x,y,z = {x2},{y2},{z2}.')
		# 	print(f'\tlat,lon,elev = {lat2},{lon2},{elev2}.')
		slope = rise / run
		steepest_slope = min(slope,steepest_slope)
		if  slope <= 0.: flattest_slope = max(slope,flattest_slope)
		elif slope > 0.: max_up_slope = max(slope,max_up_slope)
		horiz_length += run

	# Calculate some other things that depend on the sum of node-pair quantities
	total_slope = (min(firstelev,lastelev) - max(firstelev,lastelev))/horiz_length
	straight_distance = coord_distance(firstlat,firstlon,lastelev,lastlat,lastlon,lastelev)
	sinuosity = horiz_length / straight_distance
	slope_variance = -999

	# Do a little feature scaling and outlier removal
	sinuosity -= 1.0
	sinuosity /= 4.0
	
		

	data_processed[trail_id] = {'id':trail_id, 'name':trail_name, 'rating':trail_rating,
	                            'horiz_length':horiz_length, 'total_slope':total_slope,
	                            'steepest_slope':steepest_slope, 'flattest_slope':flattest_slope,
	                            'max_up_slope':max_up_slope,'sinuosity':sinuosity}

with open('data_processed.json','w') as outfile:
	json.dump(data_processed,outfile)
# The end
