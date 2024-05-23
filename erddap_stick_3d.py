import yaml
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from netCDF4 import Dataset, num2date
import requests
import tempfile
from matplotlib.colors import Normalize
from matplotlib import colormaps

def fetch_data(config):

    server_url = config['server_url']
    dataset_id = config['dataset_id']
    target_date = config['target_date']
    instrument = config['instrument']

    url = (f"{server_url}/tabledap/{dataset_id}.nc?time,depth,platform,sea_water_speed_{instrument},sea_water_direction_{instrument}&time={target_date}")
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
        depth_units = nc.variables['depth'].units
        sea_water_speed = nc.variables[f'sea_water_speed_{instrument}'][:]
        speed_units = nc.variables[f'sea_water_speed_{instrument}'].units
        sea_water_direction = nc.variables[f'sea_water_direction_{instrument}'][:]

        df = pd.DataFrame({
            'time': time_dates,
            'depth': depth,
            f'sea_water_speed_{instrument}': sea_water_speed,
            f'sea_water_direction_{instrument}': sea_water_direction
        })

        return df, depth_units, speed_units

def plot_3d_stick(df, date, instrument, depth_units, speed_units):
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
                f"Depth: {df['depth'].iloc[i]} {depth_units}<br>"
                f"Speed: {speeds.iloc[i]} {speed_units}<br>"
            )
        ))

    fig.update_layout(
        title='Sea Water Speed 3D Stick Plot for {dataset_id}',
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

    return fig

if __name__ == "__main__":
    with open('config_3d.yaml', 'r') as file:
        config = yaml.safe_load(file)
    data, depth_units, speed_units = fetch_data(config)
    if data is not None:
        fig = plot_3d_stick(data, config['target_date'], config['instrument'], depth_units, speed_units)
        fig.write_html(config['output_filename'])