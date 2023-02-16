import pandas as pd
import gpxpy
from math import sqrt,floor
from geopy import distance
import datetime
import plotly.express as px
import numpy as np
from sklearn.preprocessing import PolynomialFeatures,StandardScaler
from sklearn.linear_model import LinearRegression
gpx_file = open(r'C:\Users\MERT ÜNÜBOL\Desktop\SİHA-Workspace\Glados_yolov5_plane_detection_training\other\2017-08-05_Midnight Massacre singlespeed _Cycling.gpx', 'r')   # open the file in read mode
gpx_data = gpxpy.parse(gpx_file)

len_tracks = len(gpx_data.tracks)
len_segments = len(gpx_data.tracks[0].segments)
len_points = len(gpx_data.tracks[0].segments[0].points)

print(f"Tracks: {len_tracks} \nSegments: {len_segments} \nPoints: {len_points} \n")

gpx_points = gpx_data.tracks[0].segments[0].points

df = pd.DataFrame(columns=['lon', 'lat', 'elev', 'time']) # create a new Pandas dataframe object with give column names

# loop through the points and append their attributes to the dataframe
for point in gpx_points:
    df = df.append({'lon' : point.longitude, 'lat' : point.latitude, 'elev' : point.elevation, 'time' : point.time}, ignore_index=True)

print(f"df.head(10) displays the first 10 rows of the dataframe:\n\n{df.head(10)}\n\n")
print(f"df.info() gives a summary of the dataframe's contents and data-types:\n")
print(df.info(), "\n\n") # I had to pull this out separately because it was outputting the info table before the text, no idea why.
print(f"df.describe() gives a basic statistical summary of the numerical data:\n\n{df.describe()}")

df['time'] = df['time'].dt.tz_convert('Europe/Berlin')

df['time'] = df['time'].dt.tz_localize(None)

df.info()

df.head(10)



fig_1 = px.scatter(df, x='lon', y='lat', template='plotly_dark')

fig_1.show()

fig_2 = px.line(df, x='time', y='elev', template='plotly_dark')

fig_2.show()

fig_3 = px.scatter_3d(df, x='lon', y='lat', z='elev', color='elev', template='plotly_dark')

fig_3.update_traces(marker=dict(size=2), selector=dict(mode='markers'))

fig_3.show()
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
SEED = 42
########################################
time = np.linspace(1,207,206)
time= np.reshape(time,(-1,1))
lat = np.reshape(df['lat'].values,(-1,1))
lon = np.reshape(df['lon'].values,(-1,1))
x_train_time_lat, x_test_time_lat, y_train_lat, y_test_lat = train_test_split(time, lat, test_size=0.25, random_state=SEED)
x_train_time_lon, x_test_time_lon, y_train_lon, y_test_lon = train_test_split(time, lon, test_size=0.25, random_state=SEED)
poly_transform = PolynomialFeatures(degree=3, include_bias=False)
x_poly_train_time_lat = poly_transform.fit_transform(x_train_time_lat)
x_poly_test_time_lat = poly_transform.transform(x_test_time_lat)
x_poly_train_time_lon = poly_transform.fit_transform(x_train_time_lon)
x_poly_test_time_lon = poly_transform.transform(x_test_time_lon)
regressor_lat = make_pipeline(StandardScaler(with_mean=False), LinearRegression())
regressor_lat.fit(x_poly_train_time_lat, y_train_lat)
regressor_lon = make_pipeline(StandardScaler(with_mean=False), LinearRegression())
regressor_lon.fit(x_poly_train_time_lon, y_train_lon)
y_pred_lat = regressor_lat.predict(poly_transform.fit_transform([[212]]))
y_pred_lon = regressor_lon.predict(poly_transform.fit_transform([[212]]))
lat = np.concatenate((lat,y_pred_lat))
lon = np.concatenate((lon,y_pred_lon))

fig_5 = px.scatter_3d(df, x='lonpred', y='latpred', z='elev_pred', color='elev', template='plotly_dark')

fig_5.update_traces(marker=dict(size=2), selector=dict(mode='markers'))

fig_5.show()
fig_4 = px.line_mapbox(df, lat='lat', lon='lon', hover_name='time', mapbox_style="open-street-map", zoom=11)

fig_4.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

fig_4.show()
delta_elev = [0]    # change in elevation between records
delta_time = [0]    # time interval between records

delta_sph2d = [0]   # segment distance from spherical geometry only
delta_sph3d = [0]   # segment distance from spherical geometry, adjusted for elevation
dist_sph2d = [0]   # cumulative distance from spherical geometry only
dist_sph3d = [0]   # cumulative distance from spherical geometry, adjusted for elevation

delta_geo2d = [0]   # segment distance from geodesic method only
delta_geo3d = [0]   # segment distance from geodesic method, adjusted for elevation
dist_geo2d = [0]   # cumulative distance from geodesic method only
dist_geo3d = [0]   # cumulative distance from geodesic method, adjusted for elevation


for idx in range(1, len(gpx_points)): # index will count from 1 to lenght of dataframe, beginning with the second row
    start = gpx_points[idx-1]
    end = gpx_points[idx]

    # elevation
    temp_delta_elev = end.elevation - start.elevation
    delta_elev.append(temp_delta_elev)

    # time
    temp_delta_time = (end.time - start.time).total_seconds()
    delta_time.append(temp_delta_time)

    # distance from spherical model
    temp_delta_sph2d = distance.great_circle((start.latitude, start.longitude), (end.latitude, end.longitude)).m

    delta_sph2d.append(temp_delta_sph2d)

    dist_sph2d.append(dist_sph2d[-1] + temp_delta_sph2d)

    temp_delta_sph3d = sqrt(temp_delta_sph2d**2 + temp_delta_elev**2)

    delta_sph3d.append(temp_delta_sph3d)

    dist_sph3d.append(dist_sph3d[-1] + temp_delta_sph3d)

    # distance from geodesic model
    temp_delta_geo2d = distance.distance((start.latitude, start.longitude), (end.latitude, end.longitude)).m

    delta_geo2d.append(temp_delta_geo2d)

    dist_geo2d.append(dist_geo2d[-1] + temp_delta_geo2d)

    temp_delta_geo3d = sqrt(temp_delta_geo2d**2 + temp_delta_elev**2)

    delta_geo3d.append(temp_delta_geo3d)

    dist_geo3d.append(dist_geo3d[-1] + temp_delta_geo3d)

# dump the lists into the dataframe
df['delta_elev'] = delta_elev
df['delta_time'] = delta_time
df['delta_sph2d'] = delta_sph2d
df['delta_sph3d'] = delta_sph3d
df['dist_sph2d'] = dist_sph2d
df['dist_sph3d'] = dist_sph3d
df['delta_geo2d'] = delta_geo2d
df['delta_geo3d'] = delta_geo3d
df['dist_geo2d'] = dist_geo2d
df['dist_geo3d'] = dist_geo3d

# check bulk results
print(f"Spherical Distance 2D: {dist_sph2d[-1]/1000}km \nSpherical Distance 3D: {dist_sph3d[-1]/1000}km \nElevation Correction: {(dist_sph3d[-1]) - (dist_sph2d[-1])} meters \nGeodesic Distance 2D: {dist_geo2d[-1]/1000}km \nGeodesic Distance 3D: {dist_geo3d[-1]/1000}km \nElevation Correction: {(dist_geo3d[-1]) - (dist_geo2d[-1])} meters \nModel Difference: {(dist_geo3d[-1]) - (dist_sph3d[-1])} meters \nTotal Time: {str(datetime.timedelta(seconds=sum(delta_time)))}")

df['inst_mps'] = df['delta_geo3d'] / df['delta_time']

for threshold in np.arange(0.1, 2.1, 0.1): # delta-distance thresholds from 0 to 2 meters by 0.1 meters
    stop_time = sum(df[df['inst_mps'] < threshold]['delta_time'])
    print(f"Distance Threshold: {round(threshold,2)}m ==> {str(datetime.timedelta(seconds=stop_time))}")


df.fillna(0, inplace=True) # fill in the NaN's in the first row of distances and deltas with 0. They were breaking the overall average speed calculation
print(df['inst_mps'] >= 0.9)
df_moving = df[df['inst_mps'] >= 0.9] # make a new dataframe filtered to only records where instantaneous speed was greater than 0.9m/s

avg_mps = (sum((df['inst_mps'] * df['delta_time'])) / sum(df['delta_time']))

avg_mov_mps = (sum((df_moving['inst_mps'] * df_moving['delta_time'])) / sum(df_moving['delta_time']))

print(f"Maximum Speed: {round((2.23694 * df['inst_mps'].max(axis=0)), 2)} mph")
print(f"Average Speed: {round((2.23694 * avg_mps), 2)} mph")
print(f"Average Moving Speed: {round((2.23694 * avg_mov_mps), 2)} mph")
print(f"Moving Time: {str(datetime.timedelta(seconds=sum(df_moving['delta_time'])))}")

#filter is like map but as the name implies, it is a filter on the series you apply it to.
#If the function evaluates True, it passes the value from the series, if not, the value is skipped.
elev_gain = sum(list(filter(lambda x : x > 0, df['delta_elev'])))

print(f"Total Elevation Gain: {round(elev_gain, 2)}")  