import io
import json
import matplotlib.pyplot as plot
from mpl_toolkits.mplot3d import Axes3D
import sys

from coord_tools import lle_to_xyz_local

# Grab a trailID as a command-line argument
if len(sys.argv) == 2:
	trailid = int(sys.argv[1])
else:
	print('Need a trail ID as argument!')
	exit()

# Load data on trails and nodes
with open('data_trails.json','r') as trailfile:
	traildata = json.load(trailfile)
with open('nodes.json','r') as nodefile:
	node_lookup = json.load(nodefile)

# Find the trail the user requested
trail_info = {}
for trail in traildata['trails']:
	if str(trail['id']) == str(trailid):
		trail_info = trail
		break
	else:
		continue
if trail_info == {}:
	print('Requested trail not found!')
	exit()

# Get the coordinates of the nodes that make up the trail
node_coords = []
for nodeid in trail_info['nodes']:
	node_coords.append(node_lookup[str(nodeid)])

(firstlat,firstlon,firstelev) = node_coords[0]
#(lastlat,lastlon,lastelev) = node_coords[-1]

# Convert coordinates to x,y,z format
node_x = []
node_y =  []
node_z = []
for node in node_coords:
	(lat,lon,elev) = node
	(x,y,z) = lle_to_xyz_local(lat,lon,elev,firstlat,firstlon)
	node_x.append(x)
	node_y.append(y)
	node_z.append(z)

# Set up some drawing options
color = 'orange'
marker = '+'
if trail_info['rating'] == 'easy':
	color = 'green'
	marker = 'o'
elif trail_info['rating'] == 'intermediate':
	color = 'blue'
	marker = 's'
elif trail_info['rating'] == 'advanced':
	color = 'black'
	marker = 'd'
elif trail_info['rating'] == 'expert':
	color = 'gray'
	marker = 'd'

# Calculate appropriate plotting limits
(xmin, xmax) = (min(node_x), max(node_x))
(ymin, ymax) = (min(node_y), max(node_y))
(zmin, zmax) = (min(node_z), max(node_z))
xsize = xmax-xmin
ysize = ymax-ymin
zsize = zmax-zmin
maxsize = max([xsize,ysize,zsize])*1.1
xavg = (xmax+xmin)/2.
yavg = (ymax+ymin)/2.
zavg = (zmax+zmin)/2.
xmin = xavg - (maxsize/2.)
xmax = xavg + (maxsize/2.)
ymin = yavg - (maxsize/2.)
ymax = yavg + (maxsize/2.)
zmin = zavg - (maxsize/2.)
zmax = zavg + (maxsize/2.)


# Make the 3D plot!
fig = plot.figure()
ax = Axes3D(fig)
ax.plot(node_x, node_y, node_z, color=color, marker=marker)
ax.text(node_x[0], node_y[0], node_z[0], 'Start')
ax.text(node_x[-1], node_y[-1], node_z[-1], 'End')

ax.set_xlim(xmin,xmax)
ax.set_ylim(ymin,ymax)
ax.set_zlim(zmin,zmax)

plot.xlabel('x (meters)')
plot.ylabel('y (meters)')
ax.set_zlabel('Elevation (meters)')
plot.title(trail_info['name'])

plot.show()


