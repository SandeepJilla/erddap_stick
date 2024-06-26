# Ocean Currents Data Visualization

This Python script fetches ocean currents data from the ERDDAP server and generates stick plots for specific depths over a given time period. The script utilizes configuration parameters provided via a YAML file for easy customization and repeatability.

*Configurable Parameters*
- Data source (ERDDAP URL)
- Dataset ID
- Temporal period (start/end datestamp)
- Depth range (m)
- Color palette
- Plot dimension (width, height)
- Line spacing (2D plot)

## Requirements for 2D plot

- Python 3.x
- pandas
- matplotlib
- numpy
- pyyaml
- erddapy

*Sample Output*
![2D Plot](https://github.com/SandeepJilla/erddap_stick/blob/main/2d_plot.png)

## Requirements for 3D plot

- Python 3.x
- pandas
- plotly
- numpy
- netCDF4
- requests
- pyyaml

*Sample Output*

![3D Plot](https://github.com/SandeepJilla/erddap_stick/blob/main/3d_plot.png)

These packages can be installed using `pip`. If you do not have `pip` installed, you can get it by installing Python from [python.org](https://python.org).

## Installation

1. Clone this repository or download the script and YAML configuration file.
2. Install the required Python libraries:

```bash
pip install plotly numpy pandas netCDF4 requests matplotlib pyyaml erddapy
