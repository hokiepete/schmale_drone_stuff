# -*- coding: utf-8 -*-
"""
Created on Tue Aug 28 15:19:58 2018

@author: pnola
"""

#from mpl_toolkits.basemap import Basemap
from os import listdir
from netCDF4 import Dataset
import functions as f
from scipy.interpolate import RegularGridInterpolator
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from time import gmtime
plt.close('all')
files = listdir('wrf_les/')
interp_method = 'nearest'

xdim = 1008
ydim = 882
zdim = 20
height_level = 0
tdim = len(files)
time = np.empty([tdim])
u = np.empty([tdim,ydim,xdim])
v = np.empty([tdim,ydim,xdim])

tt=0
print(tt)
ncfile='wrf_les/'+files[tt]
root = Dataset(ncfile,'r') #read the data
vars = root.variables #dictionary, all variables in dataset
x = vars['x0'][:]*1000
y = vars['y0'][:]*1000
lon = vars['lon0'][:]
lat = vars['lat0'][:]
proj_center_lon = getattr(vars['grid_mapping_0'],'longitude_of_projection_origin')
proj_center_lat = getattr(vars['grid_mapping_0'],'latitude_of_projection_origin')
time[tt] = vars['time'][:]
u[tt,:,:] = vars['UGRD_HTGL'][0,height_level,:,:].squeeze()
v[tt,:,:] = vars['VGRD_HTGL'][0,height_level,:,:].squeeze()
root.close()

for tt in range(1,tdim):
    print(tt)
    ncfile='wrf_les/'+files[tt]
    root = Dataset(ncfile,'r') #read the data
    vars = root.variables #dictionary, all variables in dataset
    time[tt] = vars['time'][:]
    u[tt,:,:] = vars['UGRD_HTGL'][0,height_level,:,:].squeeze()
    v[tt,:,:] = vars['VGRD_HTGL'][0,height_level,:,:].squeeze()
    root.close()


speed = np.sqrt(u**2+v**2)

plt.figure(2)
plt.subplot(221)
plt.pcolormesh(x,y,speed[-1,:,:])
plt.colorbar()

plt.subplot(222)
plt.pcolormesh(x,y,u[-1,:,:])
plt.colorbar()

plt.subplot(223)
plt.pcolormesh(x,y,v[-1,:,:])
plt.colorbar()

del u,v
t0 = gmtime(time[0]).tm_hour-6
tf = gmtime(time[-1]).tm_hour-6
time = np.linspace(t0,tf,time.shape[0])

ground5 = [-106.041504,37.782005]
ground = ground5

ross_lon = np.mean([-106.04076,-106.040763,-106.040762,-106.040762])
ross_lat = np.mean([37.780287,37.780307,37.780398,37.780338])

schmale_lon = np.mean([-106.0422848,-106.0422905,-106.0422956,-106.0422941])
schmale_lat = np.mean([37.78153018,37.78155617,37.78156052,37.78156436])
#(ross, schmale)
paired_flights = [(22,9),(23,10),(25,11),(26,12)]

ground_m = f.lonlat2m(proj_center_lon,proj_center_lat,ground[0],ground[1])
ross_pos_m = f.lonlat2m(proj_center_lon,proj_center_lat,ross_lon,ross_lat)
schmale_pos_m = f.lonlat2m(proj_center_lon,proj_center_lat,schmale_lon,schmale_lat)



points = (time,y,x)
[yi,ti,xi] = np.meshgrid(ross_pos_m[1],time,ross_pos_m[0])
Xi = (ti.ravel(),yi.ravel(),xi.ravel())
fs = RegularGridInterpolator(points,speed,method=interp_method)
ross_comp_speed = fs(Xi)

[yi,ti,xi] = np.meshgrid(schmale_pos_m[1],time,schmale_pos_m[0])
Xi = (ti.ravel(),yi.ravel(),xi.ravel())
fs = RegularGridInterpolator(points,speed,method=interp_method)
schmale_comp_speed = fs(Xi)

[yi,ti,xi] = np.meshgrid(ground_m[1],time,ground_m[0])
Xi = (ti.ravel(),yi.ravel(),xi.ravel())
fs = RegularGridInterpolator(points,speed,method=interp_method)
ground_comp_speed = fs(Xi)

ground_data = pd.read_csv('Ground5_MetData.txt', delim_whitespace=True,header=1,names=['date','time','wind_speed','wind_dir','temp'])
seconds = []
for t in range(ground_data.shape[0]):
    hrs_in_sec = int(ground_data['time'][t][0:2])*3600
    min_in_sec = int(ground_data['time'][t][3:5])*60
    sec = int(ground_data['time'][t][6:8])
    seconds.append(hrs_in_sec+min_in_sec+sec)
ground_speed = ground_data['wind_speed']
ground_sec = [x/3600 for x in seconds]


ross_speed=[]
ross_sec=[]
schmale_speed=[]
schmale_sec=[]
for i, pair in enumerate(paired_flights):
    ross_data = pd.read_csv('Ross{:d}_DroneMetData.txt'.format(pair[0]), delim_whitespace=True,header=1,names=['date','time','wind_speed','wind_dir','temp'])
    seconds = []
    for t in range(ross_data.shape[0]):
        hrs_in_sec = int(ross_data['time'][t][0:2])*3600
        min_in_sec = int(ross_data['time'][t][3:5])*60
        sec = int(ross_data['time'][t][6:8])
        seconds.append(hrs_in_sec+min_in_sec+sec)
    ross_sec.append(seconds)
    ross_speed.append(ross_data['wind_speed'])
    
    schmale_data = pd.read_csv('Schmale{:d}_DroneMetData.txt'.format(pair[1]), delim_whitespace=True,header=1,names=['date','time','wind_speed','wind_dir','temp'])
    seconds = []
    for t in range(schmale_data.shape[0]):
        hrs_in_sec = int(schmale_data['time'][t][0:2])*3600
        min_in_sec = int(schmale_data['time'][t][3:5])*60
        sec = int(schmale_data['time'][t][6:8])
        seconds.append(hrs_in_sec+min_in_sec+sec)
    schmale_speed.append(schmale_data['wind_speed'])
    schmale_sec.append(seconds)

    

height = 10
width = height*1.61803398875

plt.figure(1,figsize=(width,height))
plt.subplot(311)
plt.plot(time,ground_comp_speed)
plt.plot(ground_sec,ground_speed)
plt.title('Wind speed from WRF overlaid with wind speed from ground')
#plt.xlabel('Hours since 0000hrs Mountain Time, 2018-07-17')
plt.ylabel('m/s')
plt.xlim([12,16])

plt.subplot(312)
plt.plot(time,ross_comp_speed)
for x,y in zip(ross_sec,ross_speed):
    x=[element/3600 for element in x]
    plt.plot(x,y)
plt.title('Wind speed from WRF overlaid with wind speed from Ross flights')
plt.ylabel('m/s')
plt.xlim([12,16])

plt.subplot(313)
plt.plot(time,schmale_comp_speed)
for x,y in zip(schmale_sec,schmale_speed):
    x=[element/3600 for element in x]
    plt.plot(x,y)
plt.title('Wind speed from WRF overlaid with wind speed from schmale flights')
plt.ylabel('m/s')
plt.xlim([12,16])
plt.xlabel('Hours since 0000hrs Mountain Time, 2018-07-17')
plt.savefig('speed_comparison_colorado_campaign_WRF_2018-07-17.png', transparent=False, bbox_inches='tight',pad_inches=0)
