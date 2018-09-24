# A toolbox of reusable functions involving latitude, longitude, and elevation coordinates

import math
import requests

mean_earth_radius = 6371008.8 # meters


# A simple function to request elevation data from The National Map (TNM) elevation API
# NOTE: x=longitude, y=latitude
def get_elevation(lat_y,lon_x):
	URL_EPQS = 'https://nationalmap.gov/epqs/pqs.php'
	payload={'x':lon_x,'y':lat_y,'units':'Meters','output':'json'}
	
	response = requests.get( url=URL_EPQS, params=payload )
	
	code = response.status_code
	
	if code==200:
		 myjson = response.json()
		 return myjson['USGS_Elevation_Point_Query_Service']['Elevation_Query']['Elevation']
	else:
		print(f'Error: code returned was {code}.')
		print('Message returned was:')
		if len(response.text) > 100: print('  [Not showing the really long message]')
		else: print(response.text)
		return -999

# Function to convert latitude/longitude/elevation triples to
# absolute x,y,z (i.e. the center of the earth is the origin)
def lle_to_xyz_abs(lat,lon,elev):
	# Convert elevations to ~distance from earth's center
	elev += mean_earth_radius

	# Convert latitude and longitude to radians
	lat = math.radians(lat)
	lon = math.radians(lon)

	# Find (x,y,z) coordinates
	x = elev*math.cos(lat)*math.cos(lon)
	y = elev*math.cos(lat)*math.sin(lon)
	z = elev*math.sin(lat)

	return [x, y, z]

# Transforms a point at (lat,lon,elev) to x,y,z coords in the reference
#  frame of the Earth's surface. Use the reference latitude and longitude
#  to define our origin, and sea level as z=0
def lle_to_xyz_local(lat,lon,elev,lat_ref,lon_ref):

	# First align our reference point along the x-axis (i.e. along prime meridian)
	lon -= lon_ref

	# Transform to x,y,z coordinates
	[x,y,z] = lle_to_xyz_abs(lat,lon,elev)
	# Helpful debugging output
	# print(f'Before the scary rotation, x,y,z = {x},{y},{z}')

	# Now do a (negative) 3D rotation about the y-axis
	#  by an angle theta that is the complement of the reference latitude.
	#  This will effectively put our reference point at the north pole.
	costheta = math.cos( math.radians(lat_ref-90) )
	sintheta = math.sin( math.radians(lat_ref-90) )
	# [x']   [cos  0  sin] [x]
	# [y'] = [ 0   1   0 ] [y]
	# [z']   [-sin 0  cos] [z]
	xprime = x*costheta + z*sintheta
	yprime = y
	zprime = -x*sintheta + z*costheta

	# Shift so that sea level = zero height
	zprime -= mean_earth_radius

	return [xprime,yprime,zprime]

# Calculate the Cartesian distance between two points that
#  are given in latitude/longitude/elevation space
def coord_distance(lat1,lon1,elev1,lat2,lon2,elev2):

	[x1, y1, z1] = lle_to_xyz_abs(lat1,lon1,elev1)
	[x2, y2, z2] = lle_to_xyz_abs(lat2,lon2,elev2)
	
	dist = math.sqrt( (x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2 )
	return dist

# Calculate the slope = rise/run defined by two points. First
#  requires us to shift to the reference frame of Earth's surface
def slope(lat1,lon1,elev1,lat2,lon2,elev2):

	# Arbitrarily choose point 1 to be the reference
	lat_ref = lat1
	lon_ref = lon1
	# Change lat/lon/elev to x,y,z relative to the earth's surface
	[x1, y1, z1] = lle_to_xyz_abs(lat1,lon1,elev1,lat_ref,lon_ref)
	[x2, y2, z2] = lle_to_xyz_abs(lat2,lon2,elev2,lat_ref,lon_ref)

	dist_horiz = math.sqrt( (x1-x2)**2 + (y1-y2)**2 )
	return (elev2-elev1) / dist_horiz

# Calculate the horizontal (i.e. x-y) distance between two points.
#  Again, do this in the surface reference frame
def horiz_distance(lat1,lon1,elev1,lat2,lon2,elev2):

	# Arbitrarily use point 1 as the origin
	lat_ref = lat1
	lon_ref = lon1
	# Change lat/lon/elev to x,y,z relative to the earth's surface
	[x1, y1, z1] = lle_to_xyz_abs(lat1,lon1,elev1,lat_ref,lon_ref)
	[x2, y2, z2] = lle_to_xyz_abs(lat2,lon2,elev2,lat_ref,lon_ref)

	dist_horiz = math.sqrt( (x1-x2)**2 + (y1-y2)**2 )
	return dist_horiz
