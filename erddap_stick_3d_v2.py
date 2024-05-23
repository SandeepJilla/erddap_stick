# -*- coding: utf-8 -*-
"""Untitled75.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/16bt4v9lfIMt_O0xoAVHeQ2DgdeGhbDXa
"""

import plotly.graph_objects as go
import numpy as np
import pandas as pd
from netCDF4 import Dataset, num2date
import requests
import tempfile
from matplotlib.colors import Normalize
from matplotlib import colormaps

def fetch_data(server_url, dataset_id, start_date, end_date, depth_range, instrument=0):
    url = f'{server_url}/tabledap/{dataset_id}.nc?time,latitude,longitude,depth,platform,sea_water_speed_{instrument},sea_water_direction_{instrument}&time>={start_date}&time<={end_date}'
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed to fetch data. HTTP status code: {response.status_code}")
        return None

    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(response.content)
        tmp_file.seek(0)

        try:
            nc = Dataset(tmp_file.name)
        except OSError as e:
            print(f"Failed to open NetCDF file: {e}")
            return None

        time = nc.variables['time'][:]
        time_units = nc.variables['time'].units
        time_dates = num2date(time, units=time_units)

        depth = nc.variables['depth'][:]
        sea_water_speed = nc.variables[f'sea_water_speed_{instrument}'][:]
        sea_water_direction = nc.variables[f'sea_water_direction_{instrument}'][:]

        df = pd.DataFrame({
            'time': time_dates,
            'depth': depth,
            f'sea_water_speed_{instrument}': sea_water_speed,
            f'sea_water_direction_{instrument}': sea_water_direction
        })

        df = df[(df['time'] >= pd.to_datetime(start_date)) & (df['time'] <= pd.to_datetime(end_date))]
        df = df[(df['depth'] >= depth_range[0]) & (df['depth'] <= depth_range[1])]

        return df

def plot_3d_stick(df, date, instrument=0):
    df = df[df['time'] == pd.to_datetime(date)]
    if df.empty:
        print(f"No data available for the specified date: {date}")
        return

    speeds = df[f'sea_water_speed_{instrument}']
    directions = df[f'sea_water_direction_{instrument}']

    # Convert directions to radians
    directions_rad = np.radians(directions)

    # Calculate u (eastward) and v (northward) components
    u = speeds * np.sin(directions_rad)
    v = speeds * np.cos(directions_rad)

    # Normalize speeds for color mapping
    norm = Normalize(vmin=speeds.min(), vmax=speeds.max())
    cmap = colormaps.get_cmap('viridis')
    colors = [cmap(norm(speed)) for speed in speeds]

    fig = go.Figure()

    for i in range(len(df)):
        fig.add_trace(go.Scatter3d(
            x=[7.5, u.iloc[i]],  # Starting from (0, depth, 0) and going to the u component
            y=[-2.5, v.iloc[i]],  # Starting from (0, depth, 0) and going to the v component
            z=[df['depth'].iloc[i], df['depth'].iloc[i]],  # Depth is fixed
            mode='lines',
            line=dict(color=f'rgba({colors[i][0]*255}, {colors[i][1]*255}, {colors[i][2]*255}, {colors[i][3]})', width=6),
            showlegend=False,  # Disable individual legend entries
            hovertemplate=(
                f"Date: {df['time'].iloc[i]}<br>"
                f"Depth: {df['depth'].iloc[i]} m<br>"
                f"Speed: {speeds.iloc[i]} cm/s<br>"
            )
        ))

    fig.update_layout(
        title='Sea Water Speed 3D Stick Plot',
        scene=dict(
            xaxis_title='u (Easting)',
            yaxis_title='v (Northing)',
            zaxis_title='Depth',
            xaxis=dict(showgrid=False, range=[-max(speeds), max(speeds)]),
            yaxis=dict(showgrid=False, range=[-max(speeds), max(speeds)]),
            zaxis=dict(showgrid=False, range=[df['depth'].max(), df['depth'].min()])  # Reverse the depth axis
        ),
        autosize=False,
        width=800,
        height=600
    )

    fig.show()

# Usage example
server_url = "https://erddap.gcoos.org/erddap"
dataset_id = "wmo_42881_2024"
start_date = "2024-04-08T00:00:00Z"
end_date = "2024-04-09T00:00:00Z"
depth_range = (0, 1170)
instrument = 1

data = fetch_data(server_url, dataset_id, start_date, end_date, depth_range, instrument)
if data is not None:
    plot_3d_stick(data, "2024-04-08T06:23:00Z", instrument)