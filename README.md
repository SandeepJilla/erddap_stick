# Ocean Currents Data Visualization

This Python script fetches ocean currents data from the ERDDAP server and generates stick plots for specific depths over a given time period. The script utilizes configuration parameters provided via a YAML file for easy customization and repeatability.

## Requirements for 2D plot

- Python 3.x
- pandas
- matplotlib
- numpy
- pyyaml
- erddapy

## Requirements for 3D plot

- Python 3.x
- pandas
- plotly
- numpy
- netCDF4
- requests
- pyyaml

These packages can be installed using `pip`. If you do not have `pip` installed, you can get it by installing Python from [python.org](https://python.org).

## Installation

1. Clone this repository or download the script and YAML configuration file.
2. Install the required Python libraries:

```bash
pip install plotly numpy pandas netCDF4 requests matplotlib pyyaml erddapy
