import io
import json
import math
import numpy as np
import sys

from coord_tools import lle_to_xyz_local, coord_distance, slope, horiz_distance

with open('nodes.json','r') as nodefile:
	node_lookup = json.load(nodefile)

with open('data_resorts.json','r') as resortfile:
	resort_lookup = json.load(resortfile)

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
	# Make sure node list goes from high to low (elevation)
	if firstelev < lastelev:
		[firstelev,lastelev] = [lastelev,firstelev]
		node_coord_list.reverse()

	# Do some vector math
	[xfirst,yfirst,zfirst] = lle_to_xyz_local(firstlat,firstlon,firstelev,firstlat,firstlon)
	[xlast,ylast,zlast] = lle_to_xyz_local(lastlat,lastlon,lastelev,firstlat,firstlon)
	chord_flat = np.array([xlast-xfirst, ylast-yfirst, 0]) # Vector from start to finish, projected on to x-y plane
	perp_flat = np.array([yfirst-ylast, xlast-xfirst, 0]) # Vector perpendicular to the above

	horiz_length = 0.
	total_length = 0.
	max_slope = -999.
	min_slope = 999.
	inflections = -1
	previous_sign = 0
	#north_south_asymmetry = -999


	# Loop through node pairs and calculate various quantities
	# Always go from highest node to lowest node, regardless of storage order
	for i in range(0,num_nodes-1):
		[lat1,lon1,elev1] = node_coord_list[i]
		[lat2,lon2,elev2] = node_coord_list[i+1]
		if [lat1,lon1] == [lat2,lon2]: continue # Avoid duplicate nodes
		[x1,y1,z1] = lle_to_xyz_local(lat1,lon1,elev1,firstlat,firstlon)
		[x2,y2,z2] = lle_to_xyz_local(lat2,lon2,elev2,firstlat,firstlon)
		rise = z1-z2
		run = math.sqrt( (x1-x2)**2 + (y1-y2)**2 )
		slope = rise / run
		max_slope = max(slope,max_slope)
		min_slope = min(slope,min_slope)
		horiz_length += run
		total_length += math.sqrt( run*run + rise*rise )

		vector = np.array([x2-x1,y2-y1,0]) # Vector from p1 to p2, projected onto x-y plane
		dotproduct = np.dot(vector,perp_flat)
		sign = np.sign(dotproduct)
		if sign*previous_sign <= 0:
			inflections += 1
			previous_sign = sign

	# Calculate some other things that depend on the sum of node-pair quantities
	# if abs(min_slope) > max_slope: min_slope = 0.0
	if min_slope < 0.: min_slope = 0.
	total_slope = (firstelev-lastelev)/horiz_length
	flat_distance = coord_distance(firstlat,firstlon,lastelev,lastlat,lastlon,lastelev)
	straight_distance = coord_distance(firstlat,firstlon,firstelev,lastlat,lastlon,lastelev)
	sinuosity = total_length / straight_distance
	if total_slope == 0: continue
	slope_spread = (max_slope - min_slope) #/  total_slope
	inflections_per_km = 1000. * inflections / total_length

	# Make some cuts
	if total_length < 100.0: continue
	if num_nodes <3: continue

	# Find the best-matched resort/mountain/ski area
	minprio = 99.
	best_resort_name = "Unknown"
	best_resort_id = -999999
	for node in resort_lookup['elements']:
		if 'shop' in node['tags'].keys(): continue
		if 'aerialway' in node['tags'].keys(): continue
		if 'rental' in node['tags']['name'].lower(): continue
		rlat = node['lat']
		rlon = node['lon']
		if abs( rlat - lastlat ) > 1.: continue
		if abs( rlon - lastlon ) > 1.: continue
		dist = coord_distance(lastlat,lastlon,lastelev,rlat,rlon,lastelev)
		if dist > 1000.: continue
		resort_name = node['tags']['name']
		resort_id = node['id']
		resort_dist = dist
		# Try to rate the various matches on some kind of priority
		prio = 999
		if 'site' in node['tags'] and node['tags']['site'] == 'piste':
			if dist < 100.: prio = dist/100.
			else: prio = 1. + (dist/1000.)
		elif 'leisure' in node['tags'] and  node['tags']['leisure'] == 'sports_centre':
			if 'ski' in node['tags']['name'].lower() and dist < 200.: prio = 2.
			elif dist < 300.: prio = 2.5
			else: prio = 3.
		elif 'resort' in node['tags']['name'].lower() and dist < 350.: prio = 2.3
		elif 'mountain' in node['tags']['name'].lower(): prio = 4.
		elif dist > 500.: continue
		elif 'peak' in node['tags']['name'].lower(): prio = 5.
		elif 'valley' in node['tags']['name'].lower(): prio = 6.
		else: continue

		if prio < minprio:
			minprio = prio
			[best_resort_name,best_resort_id] = [resort_name,resort_id]


	# Do a little feature scaling and outlier removal
	feat_sinu = (sinuosity-1.0)/4.0
	feat_spread = slope_spread / 1.5
	feat_inflect = inflections / 20.
	feat_length = horiz_length / 3000.

	if feat_sinu > 1.0: continue
	if feat_spread > 1.0: continue
	if feat_inflect > 1.0: continue
	if feat_length > 1.0: continue
	
	count += 1

	data_processed[trail_id] = {'id':trail_id, 'name':trail_name, 'rating':trail_rating,
	                            'horiz_length':horiz_length, 'total_length':total_length,
	                            'total_slope':total_slope, 'slope_spread':slope_spread,
	                            'max_slope':max_slope, 'min_slope':min_slope,
	                            'sinuosity':sinuosity, 'inflect':inflections,
	                            'resort_id':best_resort_id, 'resort_name':best_resort_name,
	                            'feat_sinu':feat_sinu, 'feat_spread':feat_spread,
	                            'feat_inflect':feat_inflect, 'feat_length':feat_length}

with open('data_processed.json','w') as outfile:
	json.dump(data_processed,outfile)

print(f'Saved {count} trails to data_processed.json.')
# The end
