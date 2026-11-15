# Project Ares-Luna
## The Kepler 5

The web app currently runs a similarity algorithm between data on **Earth** (currently junk) and **Mars** (scraped from NASA databases and averaged).

### To run:

If `uv` is not installed, do so:
*Unix:*
```bash
curl -LsSf https://astral.sh | sh
```
*Windows (Run):*
```powershell
powershell -c "irm https://astral.sh | iex"
```

Clone the repository if not done already, and sync the virtual environment via:
```bash
uv sync
```

To run:
```bash
uv run streamlit run app.py
```
 ## datasets used:
  elevation datasets are referenced from [NASA's MOLA recordings](https://pds-geosciences.wustl.edu/mgs/urn-nasa-pds-mgs_mola_topography_derived/meg128/)
  temperature datasets are referenced from [NASA's THEMIS recordings](https://ode.rsl.wustl.edu/mars/productsearch)
  all moon datasets are referenced from [NASA's LOLA recordings](https://imbrium.mit.edu/DATA/LOLA_GDR/POLAR/IMG/)

## ⭐ data processing:

during this project, we quickly realised the data we required from NASA required processing and compiling into a comprehensive format for use within the web-app.

using one script for Mars [(mars_data.py)](spaceapp-challenge/scripts/mars_data.py) and another for the moon's elevation [(moon_elevation)](spaceapp-challenge/scripts/moon_elevation.py) and utilizing the Rasterio Python library for extended versatility rather than using QGIS, we were able to understand more behind NASA's data. 

### @salxish's input:
>intitially we began with trying to process Shackleton Crater's topology data to develop an understanding of how to process such data using Python whilst learning Rasterio knowing the focus was on Mars' Crater's. familiarising my self with processing datasets of this variety allowed me to collaborate further with my team moving past solely reproducible slope and elevation data and expanding towards infrared temperature data.

>the decision to not use QGIS did slow progression of the project, but it's incredibly important to understand the following: NASA's THEMIS and MOLA record data with variations between formatting. in figuring out how to use Python and Rasterio to process elevation and temperature, we were able to recognise similarities in the slope and temperature of the craters and better compare them to similar locations on Earth by coordinates. 
