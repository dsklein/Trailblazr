import io
import json
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys

# If using affinity propagation
# from sklearn.cluster import AffinityPropagation
# from sklearn import metrics

# If using mean shift
# from sklearn.cluster import MeanShift, estimate_bandwidth

# If using DBSCAN
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler


# Function to calculate the proximity (in slope,sinuosity space) of two trails
def proximity(a,b):
	dx = a['slope'] - b['slope']
	dy = a['sinuosity'] - b['sinuosity']
	return math.sqrt( dx*dx + dy*dy )


# Read json into dataframe
print('Loading data from json file...')
df = pd.read_json('data_processed.json')

# Transpose dataframe
df = df.T

# Pick out only the features of interest
df2 = df[['total_slope','feat_sinu','feat_length','feat_inflect','feat_spread']]
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
# 0.2      20             4       7662,  1939,  498,  287,  15
# 0.4      30             5       6032,  2710,  893,  715,  31,   20
# 0.4      20             6       5117,  1082, 2983,  1038, 145,  21,  15

# Do clustering using DBSCAN
df2 = StandardScaler().fit_transform(df2)
db = DBSCAN(eps=0.4, min_samples=20).fit(df2) ##########################
core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
core_samples_mask[db.core_sample_indices_] = True
labels = db.labels_
labellist, labelcounts = np.unique(labels, return_counts=True)
print(f'Labels is type {type(labels)} and has shape {labels.shape}.')
n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
print(f'Found {n_clusters_} clusters.')

unique_labels = set(labels)
colors = [plt.cm.Spectral(each)
          for each in np.linspace(0, 1, len(unique_labels))]
for k, col in zip(unique_labels, colors):
    if k == -1:
        # Black used for noise.
        col = [0, 0, 0, 0.1]
	    #continue

    class_member_mask = (labels == k)
    print(f'Cluster {k}: members={labelcounts[k]}')

    xy = df2[class_member_mask & core_samples_mask]
    plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=tuple(col),
             markeredgecolor='k', markersize=14)

    xy = df2[class_member_mask & ~core_samples_mask]
    plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=tuple(col),
             markeredgecolor='k', markersize=6)

plt.title('Estimated number of clusters: %d' % n_clusters_)
plt.xlabel('Total Slope')
plt.ylabel('Sinuosity')
plt.savefig('../pictures/clusters_DBSCAN.png')
print('Saved plot in ../pictures/clusters_DBSCAN.png')
plt.show()

######################################################

# Output the data from our dataframe (and associated labels)
slope_dict = {}
count = 0
for i,row in df3.iterrows():
	nodeid = i
	name = df['name'][nodeid]
	rating = df['rating'][nodeid]
	resortname = df['resort_name'][nodeid]
	resortid = df['resort_id'][nodeid]
	slope = row['total_slope'] ##########################
	sinu  = row['sinuosity'] ############################
	length = row['total_length']
	inflect = row['inflect']
	spread = row['slope_spread']
	label = int(labels[count])
	# Somehow get nearest neighbors!
	slope_dict[nodeid] = {'id':nodeid, 'name':name, 'label':label,
	                      'rating':rating,'slope':slope, 'sinuosity':sinu,
	                      'length':length, 'inflect':inflect, 'spread':spread,
	                      'resort_name':resortname, 'resort_id':resortid}
	count += 1

# Loop back through our new dict of trails, and find a bunch of
#  neighbors for every trail
print('Finding nearest neighbors...')
for id in slope_dict.keys():
	neighborhood = []
	for jd in slope_dict.keys():
		if slope_dict[jd]['label'] != slope_dict[id]['label']: continue
		if id == jd: continue
		prox = proximity(slope_dict[id], slope_dict[jd])
		if prox > 0.05: continue
		neighborhood.append( (jd,prox) )
	neighborhood.sort(key=lambda a: a[1])
	slope_dict[id]['neighbors'] = neighborhood[:10]

	# Would also be nice to find neighbors at the same resort

with open('labeled_results.json','w') as outfile:
	json.dump(slope_dict,outfile)
print('Wrote labeled data to labeled_results.json.')
