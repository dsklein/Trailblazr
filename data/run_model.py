import io
import json
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys

from coord_tools import coord_distance

# If using affinity propagation
# from sklearn.cluster import AffinityPropagation
# from sklearn import metrics

# If using mean shift
# from sklearn.cluster import MeanShift, estimate_bandwidth

# If using DBSCAN
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler, QuantileTransformer, KBinsDiscretizer


# Function to calculate the proximity (in slope,sinuosity space) of two trails
def proximity(a,b):
	dx = a['slope'] - b['slope'] # Min-max ~1
	dy = a['sinuosity'] - b['sinuosity'] # Width ~1
	dz = (a['length'] - b['length']) / 2000.
	dv = (a['inflect'] - b['inflect']) / 15.
	dw = (a['spread'] - b['spread']) / 0.5
	return math.sqrt( dx*dx + dy*dy + dz*dz + dv*dv + dw*dw )


# Read json into dataframe
print('Loading data from json file...')
df = pd.read_json('data_processed.json')

# Transpose dataframe
df = df.T

# Pick out only the features of interest
df2 = df[['total_slope','sinuosity','total_length','inflect','slope_spread']]
df3 = df.copy(deep=True)

######################################################


# # Do the clustering using affinity propagation
# print('Running clustering...')
# af = AffinityPropagation(verbose=True).fit(df2)
# cluster_centers_indices = af.cluster_centers_indices_
# labels = af.labels_
# n_clusters_ = len(cluster_centers_indices)
# print(f'Found {n_clusters} clusters.')

######################################################

# Estimate bandwidth and cluster using mean shift
# print('Estimating bandwidth...')
# bandwidth = estimate_bandwidth(df2, quantile=0.2, n_samples=6000, n_jobs=2)
# print(f'Bandwidth chosen to be {bandwidth}.')
# print('Running clustering...')
# ms = MeanShift(bandwidth=bandwidth, bin_seeding=True)
# # ^ Consider setting bin_seeding = True (will speed up bandwith finding)
# # ^ Also consider setting min_bin_freq to some number > 1 (will only seed on higher bins)
# ms.fit(df2)
# labels = ms.labels_
# cluster_centers = ms.cluster_centers_
# labels_unique = np.unique(labels)
# n_clusters_ = len(labels_unique)
# print(f'Found {n_clusters_} clusters.')
# print(cluster_centers)

# # Now do the plotting
# from itertools import cycle

# plt.figure(1)
# plt.clf()
# plt.figure(2)
# plt.clf()

# colors = cycle('bgrcmykbgrcmykbgrcmykbgrcmyk')
# for k, col in zip(range(n_clusters_), colors):
#     my_members = labels == k
#     cluster_center = cluster_centers[k]
#     print(f'Cluster {k} has {len(df2[my_members])} members.')
#     # print(f'\tCenter = ({cluster_center[0]},{cluster_center[1]})')
#     plt.figure(1)
#     plt.plot(df2[my_members]['total_slope'], df2[my_members]['feat_sinu'], col + '.')
#     plt.plot(cluster_center[0], cluster_center[1], 'o', markerfacecolor=col,
#              markeredgecolor='k', markersize=14)
#     plt.figure(2)
#     plt.plot(df2[my_members]['feat_inflect'], df2[my_members]['feat_length'], col + '.')
#     plt.plot(cluster_center[3], cluster_center[2], 'o', markerfacecolor=col,
#              markeredgecolor='k', markersize=14)
# plt.figure(1)
# plt.title('Estimated number of clusters: %d' % n_clusters_)
# plt.xlabel('Total Slope')
# plt.ylabel('Sinuosity (adjusted)')
# plt.savefig('../pictures/clusters_slope_sinu.png')
# print('Saved plot in ../pictures/clusters_slope_sinu.png')
# plt.figure(2)
# plt.title('Estimated number of clusters: %d' % n_clusters_)
# plt.xlabel('Inflections')
# plt.ylabel('Horizontal Length')
# plt.savefig('../pictures/clusters_inflect_hlength.png')
# print('Saved plot in ../pictures/clusters_inflect_hlength.png')
# # plt.show()

######################################################

# eps   min_samples   n_clusters  cluster sizes
# Using StandardScaler
# 0.2      20             4       7662,  1939,  498,  287,  15
# 0.4      30             5       6032,  2710,  893,  715,  31,   20
# 0.4      20             6       5117,  1082, 2983,  1038, 145,  21,  15
# Using QuantileTransformer
#
# Using KBinsDiscretizer
# nbins=3, encode=ordinal, strategy=uniform: 10 clusters, 41 outliers, n0 = 7486, n1=2202

# Do clustering using DBSCAN
# df2 = StandardScaler().fit_transform(df2)
# df2 = QuantileTransformer(n_quantiles=10).fit_transform(df2)
df2 = KBinsDiscretizer(n_bins=3, encode='ordinal', strategy='uniform').fit_transform(df2)
db = DBSCAN(eps=0.4, min_samples=10).fit(df2) ##########################
core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
core_samples_mask[db.core_sample_indices_] = True
labels = db.labels_
labellist, labelcounts = np.unique(labels, return_counts=True)
print(f'Labels is type {type(labels)} and has shape {labels.shape}.')
n_clusters_ = len(labellist) - (1 if -1 in labels else 0)
print(f'Found {n_clusters_} clusters.')

# Make plots of the clusters
unique_labels = labellist
feature_names = ['Total Slope', 'Curvature', 'Length', 'Turns per km', 'Variation in Slope']
features_short = ['totalslope', 'sinuosity', 'totallength', 'inflections', 'slopespread']
for i in range(0, len(feature_names)):
	colors = [plt.cm.Spectral(each) for each in np.linspace(0, 1, len(unique_labels))]
	for k, col in zip(unique_labels, colors):
		if k == -1: col = [0, 0, 0, 0.1] # Black used for noise.

		class_member_mask = (labels == k)
		num_members = labelcounts[list(labellist).index(k)]
		if i==0: print(f'Cluster {k}: members={num_members}')

		xy = df2[class_member_mask & core_samples_mask]
		plt.plot(xy[:, i-1], xy[:, i], 'o', markerfacecolor=tuple(col),
		         markeredgecolor='k', markersize=14)

		xy = df2[class_member_mask & ~core_samples_mask]
		plt.plot(xy[:, i-1], xy[:, i], 'o', markerfacecolor=tuple(col),
		         markeredgecolor='k', markersize=6)

	plt.title('Estimated number of clusters: %d' % n_clusters_)
	plt.xlabel(feature_names[i-1])
	plt.ylabel(feature_names[i])
	plt.savefig('../pictures/clusters_DBSCAN_'+features_short[i]+'_vs_'+features_short[i-1]+'.png')
	print('Saved plot in ../pictures/clusters_DBSCAN_'+features_short[i]+'_vs_'+features_short[i-1]+'.png')
	# plt.show()
	plt.clf()

######################################################

# Output the data from our dataframe (and associated labels)
slope_dict = {}
count = 0
# difficulty_comparison = []
# for label in unique_labels: difficulty_comparison.append( {'total':0, 'easy':0, 'intermediate':0, 'advanced':0, 'expert':0} )
histlist_cluster = [ [],[],[],[] ]
difficulty_mapper = {'easy':0, 'intermediate':1, 'advanced':2, 'expert':3}
colors = ['green','blue','black','gray']
difficulties = ['Easy','Intermediate','Advanced','Expert']

for i,row in df3.iterrows():
	nodeid = i
	# Not features
	name = df['name'][nodeid]
	rating = df['rating'][nodeid]
	resortname = df['resort_name'][nodeid]
	resortid = df['resort_id'][nodeid]
	state = df['state'][nodeid]
	last_coord = df['last_coord'][nodeid]
	# Features (and label)
	slope = row['total_slope']
	sinu  = row['sinuosity']
	length = row['total_length']
	inflect = row['inflect']
	spread = row['slope_spread']
	label = int(labels[count])
	slope_dict[nodeid] = {'id':nodeid, 'name':name, 'label':label,
	                      'last_coord':last_coord,
	                      'rating':rating,'slope':slope, 'sinuosity':sinu,
	                      'length':length, 'inflect':inflect, 'spread':spread,
	                      'resort_name':resortname, 'resort_id':resortid, 'state':state}
	count += 1
	diff_level = difficulty_mapper[rating]
	histlist_cluster[diff_level].append(label)

# Make a comparison of the trail ratings in each cluster
n,bins,patches = plt.hist(x=histlist_cluster, bins=len(labellist), stacked='true', density='true', color=colors, label=difficulties)
plt.xlabel('Cluster')
plt.ylabel('Fraction')
plt.title('Cluster composition')
plt.legend(loc='upper right')
# plt.show()
plt.savefig('../pictures/cluster_composition.png')
print('Saved ../pictures/cluster_composition.png')


# Loop back through our new dict of trails, and find a bunch of
#  neighbors for every trail
print('Finding nearest neighbors...')
for id in slope_dict.keys():
	neighborhood_nat = []
	neighborhood_loc = []
	for jd in slope_dict.keys():
		#if slope_dict[jd]['label'] != slope_dict[id]['label']: continue
		if id == jd: continue
		prox = proximity(slope_dict[id], slope_dict[jd])
		if prox <= 0.5:
			neighborhood_nat.append( (jd,prox) )
		[lat1,lon1,elev1] = slope_dict[id]['last_coord']
		[lat2,lon2,elev2] = slope_dict[jd]['last_coord']
		dist = coord_distance(lat1,lon1,elev1,lat2,lon2,elev2)
		if dist < 100.*1600. and prox <= 0.5:
			neighborhood_loc.append( (jd,prox,dist) ) # 100 miles
	neighborhood_nat.sort(key=lambda a: a[1])
	neighborhood_loc.sort(key=lambda a: a[1])
	slope_dict[id]['neighbors_usa'] = neighborhood_nat[:10]
	slope_dict[id]['neighbors_near'] = neighborhood_loc[:10]

with open('labeled_results.json','w') as outfile:
	json.dump(slope_dict,outfile)
print('Wrote labeled data to labeled_results.json.')
