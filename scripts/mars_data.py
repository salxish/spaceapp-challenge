# elev datasets are referenced from NASA's MOLA recordings (https://pds-geosciences.wustl.edu/mgs/urn-nasa-pds-mgs_mola_topography_derived/meg128/)
# temp datasets are referenced from NASA's THEMIS recordings (https://ode.rsl.wustl.edu/mars/productsearch)
# due to slight changes in calculation, min_temp also refers towards temp_k (temperature in kelvins)

import pandas as pd
import numpy as np
from pyproj import Transformer
import rasterio


def csv_gen(gale, jezero, gale_temps, jezero_temps):
    print("CSV generating.")
    rows = []
    for n, t in enumerate(gale_temps, 1):
        rows.append(dict(site=f"Gale Crater {n}", coords="5.4°S, 137.8°E", slope_degree=round(gale, 2),
                         pixel_size_const=463, min_temp=round(t, 2), rain_mm=0, albedo=None))
    for n, t in enumerate(jezero_temps, 1):
        rows.append(dict(site=f"Jezero Crater {n}", coords="18.41°N, 77.69°E", slope_degree=round(jezero, 2),
                         pixel_size_const=463, min_temp=round(t, 2), rain_mm=0, albedo=None))
    pd.DataFrame(rows).to_csv("mars_data.csv", index=False)
    print("saved CSV.")

def gale_crater_elev():
    # Gale Crater (estim 5.4°S, 137.8°E)
    R, PPD = 3396200, 128
    px = 2 * np.pi * R / 360 / PPD

    with rasterio.open("../NASA_images/elevations/megt00n090hb.LBL") as src:
        raw_data = src.read()
        print("Preliminary data check:")
        print(src.shape, src.dtypes, src.res, src.scales, src.offsets)

    with rasterio.open("../NASA_images/elevations/megt00n090hb.LBL") as src:
        raw = src.read(1).astype("float64")
        scale = src.scales[0]
        print("Data stage 1:")
        print(raw, scale)
        if src.nodata is not None:
            raw[raw == src.nodata] = np.nan

    # the values are currently raw ints, raw*scale converts to metres
    elev = raw * scale
    print("Data stage 2:")
    print(elev.shape, np.nanmin(elev), np.nanmax(elev))

    # locates the gale crater
    ci = int((0 - (-5.4)) * PPD)
    cj = int((137.8 - 90) * PPD)

    h = int(30000 / px)
    sub = elev[ci - h:ci + h, cj - h:cj + h]
    ci2 = cj2 = h

    dy, dx = np.gradient(sub, px)
    slope = np.degrees(np.arctan(np.hypot(dx, dy)))

    rows, cols = np.indices(sub.shape)
    mask = np.hypot(rows - ci2, cols - cj2) < 25000 / px
    mean_slope = np.nanmean(slope[mask])
    print("Slope:", mean_slope)
    return mean_slope

def jezero_crater_elev():
    # Jezero Crater (estim 18.41°N, 77.69°E)
    R, PPD = 3396200, 128
    px = 2 * np.pi * R / 360 / PPD

    with rasterio.open("../NASA_images/elevations/megt44n000hb.LBL") as src:
        raw_data = src.read()
        print("Preliminary data check:")
        print(src.shape, src.dtypes, src.res, src.scales, src.offsets)

    with rasterio.open("../NASA_images/elevations/megt44n000hb.LBL") as src:
        raw = src.read(1).astype("float64")
        scale = src.scales[0]
        print("Data stage 1:")
        print(raw, scale)
        if src.nodata is not None:
            raw[raw == src.nodata] = np.nan

    # the values are currently raw ints, raw*scale converts to metres
    elev = raw * scale
    print("Data stage 2:")
    print(elev.shape, np.nanmin(elev), np.nanmax(elev))

    # locates the jezero crater
    ci = int((44 - 18.41) * PPD)
    cj = int((77.69 - 0) * PPD)

    h = int(30000 / px)
    sub = elev[ci - h:ci + h, cj - h:cj + h]
    ci2 = cj2 = h

    dy, dx = np.gradient(sub, px)
    slope = np.degrees(np.arctan(np.hypot(dx, dy)))

    rows, cols = np.indices(sub.shape)
    mask = np.hypot(rows - ci2, cols - cj2) < 25000 / px
    mean_slope = np.nanmean(slope[mask])
    print("Slope:", mean_slope)
    return mean_slope

def gale_crater_temp():
   # with a better understanding, now scaffolding from jezero_crater_temp()
   images = ["../NASA_images/temps/gale/i82284019pbt.xml", "../NASA_images/temps/gale/ia73xxpbt/ia7398004pbt.xml",
    "../NASA_images/temps/gale/i991xxpbt/i99187022pbt.xml", "../NASA_images/temps/gale/i990xxpbt/i99019001pbt.xml",
    "../NASA_images/temps/gale/i989xxpbt/i98994001pbt.xml", "../NASA_images/temps/gale/i905xxpbt/i90521001pbt.xml",
    "../NASA_images/temps/gale/i825xxpbt/i82547001pbt.xml", "../NASA_images/temps/gale/i823xxpbt/i82310001pbt.xml",
    "../NASA_images/temps/gale/i822xxpbt/i82260001pbt.xml"]
   results = []
   for path in images:
        with rasterio.open(path) as src:
            raw_data = src.read()
            print("Preliminary data check:")
            print(src.crs, src.bounds, src.res, src.nodata, src.scales, src.offsets)

        with rasterio.open(path) as src:
            raw = src.read(1).astype("float64")
            print("Data stage 1:")
            if src.nodata is not None:
                raw[raw == src.nodata] = np.nan
            raw[raw == 0] = np.nan
            # this time it's for the right temperature unit (Kelvin)
            temp = raw * src.scales[0] + src.offsets[0]

            # slight difference in processing, THEMIS utils x/y instead of pixels :(
            to_proj = Transformer.from_crs("+proj=longlat +R=3396190 +no_defs", src.crs, always_xy=True)
            x, y = to_proj.transform(137.8, -5.4)
            r, c = src.index(x, y)

        print("Data stage 2:")
        if not (0 <= r < temp.shape[0] and 0 <= c < temp.shape[1]):
            print(path, "- site is outside this image, skipped")
            continue
        print("Pixel:", r, c, "Temp (K):", temp[r, c])

        h = 770 # wider range than jezero
        window = temp[max(r - h, 0):r + h, max(c - h, 0):c + h]
        if np.all(np.isnan(window)):
            print("no data at", path, "so skip")
            continue
        mean_temp = np.nanmin(window)
        print("Data stage 3:")
        print("Temp:", mean_temp)
        results.append(mean_temp)

   return results

def jezero_crater_temp():
    images = ["../NASA_images/temps/jezero/ia7356002pbt.xml",
              "../NASA_images/temps/jezero/i991xxpbt/i99164005pbt.xml", "../NASA_images/temps/jezero/i991xxpbt/i99120007pbt.xml", 
              "../NASA_images/temps/jezero/i990xxpbt/i99095006pbt.xml", "../NASA_images/temps/jezero/i988xxpbt/i98877005pbt.xml", 
              "../NASA_images/temps/jezero/i906xxpbt/i90666009pbt.xml", "../NASA_images/temps/jezero/i824xxpbt/i82455008pbt.xml", 
              "../NASA_images/temps/jezero/i824xxpbt/i82430009pbt.xml"]
    results = []
    for path in images:
        with rasterio.open(path) as src:
            raw_data = src.read()
            print("Preliminary data check:")
            print(src.crs, src.bounds, src.res, src.nodata, src.scales, src.offsets)

        with rasterio.open(path) as src:
            raw = src.read(1).astype("float64")
            print("Data stage 1:")
            if src.nodata is not None:
                raw[raw == src.nodata] = np.nan
            raw[raw == 0] = np.nan
            # this time it's for the right temperature unit (Kelvin)
            temp = raw * src.scales[0] + src.offsets[0]

            # slight difference in processing, THEMIS utils x/y instead of pixels :(
            to_proj = Transformer.from_crs("+proj=longlat +R=3396190 +no_defs", src.crs, always_xy=True)
            x, y = to_proj.transform(77.69, 18.41)
            r, c = src.index(x, y)

        print("Data stage 2:")
        if not (0 <= r < temp.shape[0] and 0 <= c < temp.shape[1]):
            print(path, "- site is outside this image, skipped")
            continue
        print("Pixel:", r, c, "Temp (K):", temp[r, c])

        h = 180 # reasonable tbf
        mean_temp = np.nanmin(temp[r - h:r + h, c - h:c + h])
        print("Data stage 3:")
        print("Temp:", mean_temp)
        if np.isnan(mean_temp):
            print("no data at", path, "so skip")
            continue
        results.append(mean_temp)
    return results

if __name__ == "__main__":
    gale = gale_crater_elev()
    jezero = jezero_crater_elev()
    gale_temps = gale_crater_temp()
    jezero_temps = jezero_crater_temp()
    csv_gen(gale, jezero, gale_temps, jezero_temps)

