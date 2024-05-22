import plotly.graph_objects as go
import numpy as np
import pandas as pd
from netCDF4 import Dataset, num2date
import requests
import tempfile
import yaml

def fetch_data(config):

    server_url = config['server_url']
    dataset_id = config['dataset_id']
    start_date = config['start_date']
    end_date = config['end_date']
    depth_range = tuple(config['depth_range'])
    color_pallete = config['color_pallete']
    instrument = config['instrument']

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

        df = df.dropna(subset=[f'sea_water_speed_{instrument}', f'sea_water_direction_{instrument}'])

        if df.empty:
            print(f"No data available for depths between {depth_range[0]}m and {depth_range[1]}m for instrument {instrument}")
            return

        df = df[(df['time'] >= pd.to_datetime(start_date)) & (df['time'] <= pd.to_datetime(end_date))]
        df = df[(df['depth'] >= depth_range[0]) & (df['depth'] <= depth_range[1])]

        return df

def plot_3d_stick(df, instrument=0):
    speeds = df[f'sea_water_speed_{instrument}']
    directions = df[f'sea_water_direction_{instrument}']

    # Convert directions to radians
    directions_rad = np.radians(directions)

    # Calculate u (eastward) and v (northward) components
    u = speeds * np.sin(directions_rad)
    v = speeds * np.cos(directions_rad)

    # Define color palette
    color_palette = ['pink', 'skyblue', 'green', 'yellow', 'orange', 'red']
    colors = np.where(speeds <= 10, color_palette[0],
                      np.where(speeds <= 20, color_palette[1],
                               np.where(speeds <= 30, color_palette[2],
                                        np.where(speeds <= 40, color_palette[3],
                                                 np.where(speeds <= 50, color_palette[4], color_palette[5])))))

    fig = go.Figure()

    # Create a single trace for all sticks
    for i in range(len(df)):
        fig.add_trace(go.Scatter3d(
            x=[df['time'].iloc[i], df['time'].iloc[i]],
            y=[df['depth'].iloc[i], df['depth'].iloc[i] + u.iloc[i]],
            z=[0, abs(v.iloc[i])],  # Using the absolute value of z-component for speed
            mode='lines',
            line=dict(color=colors[i], width=6),
            showlegend=False,  # Disable individual legend entries
            hovertemplate=(
                f"Date: {df['time'].iloc[i]}<br>"
                f"Depth: {df['depth'].iloc[i]}<br>"
                f"Speed: {speeds.iloc[i]}<br>"
                # f"Direction Angle: {directions.iloc[i]} degrees"
            )
        ))

    # Add custom legend items in the correct order
    speed_ranges = ['Speed > 50', 'Speed > 40 and <= 50', 'Speed > 30 and <= 40',
                    'Speed > 20 and <= 30', 'Speed > 10 and <= 20', 'Speed <= 10']

    for i, label in enumerate(reversed(speed_ranges)):
        fig.add_trace(go.Scatter3d(
            x=[None],
            y=[None],
            z=[None],
            mode='lines',
            line=dict(color=color_palette[i], width=6),
            showlegend=True,
            name=label
        ))

    fig.update_layout(
        title='Sea Water Speed 3D Stick Plot',
        scene=dict(
            xaxis_title='Date',
            yaxis_title='Depth',
            zaxis_title='Speed',
            xaxis=dict(type='date')
        ),
        autosize=False,
        width=800,
        height=600,
        legend=dict(title='Speed Legend (cm s-1)', itemsizing='constant')
    )

    return fig

if __name__ == "__main__":
    with open('config_3d_plot.yaml', 'r') as file:
        config = yaml.safe_load(file)
        data = fetch_data(config)
        if data is not None:
            fig = plot_3d_stick(data, config['instrument'])
            fig.write_html('3d_plot.html')
