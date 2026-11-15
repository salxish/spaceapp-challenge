# all datasets are referenced from NASA's LOLA recordings (https://imbrium.mit.edu/DATA/LOLA_GDR/POLAR/IMG/)
# Shackleton Crater (estim 89.67°S, 129.78°E)

import matplotlib.pyplot as plt
import numpy as np
import rasterio

with rasterio.open("../NASA_images/elevations/LDEM_80S_20M.LBL") as src:
    raw_data = src.read(1)
    print("Preliminary data check:")
    print(src.shape, src.dtypes, src.res, src.scales, src.offsets)

with rasterio.open("../NASA_images/elevations/LDEM_80S_20M.LBL") as src:
    raw = src.read(1).astype("float64")
    px = src.res[0]
    scale = src.scales[0]
    print("Data stage 1:")
    print(raw,px,scale)
    if src.nodata is not None:
        raw[raw == src.nodata] = np.nan

# the values are currently raw ints, raw*scale converts to metres
elev = raw * scale

# visualisation for 60km * 60km area of Moon's South Pole.
i0,  j0 = elev.shape[0] // 2, elev.shape[1] // 2
h = int(30000 / px)
sub = elev[i0-h:i0+h,j0-h:j0+h]
print("Data stage 2:")
print(np.nanmin(sub), np.nanmax(sub)) # account for relief

# focusing on the centre of the Shackleton Crater
plt.imshow(sub, cmap="gray"); plt.colorbar()
pts = plt.ginput(1)
plt.close()
if not pts:
    raise SystemExit("No centre click given.")
cj, ci = pts[0]
ci, cj = int(ci), int(cj)
print("centre of crater:",ci, cj)

dy, dx = np.gradient(sub, px)
slope = np.degrees(np.arctan(np.hypot(dx, dy)))

rows, cols = np.indices(sub.shape)
mask = np.hypot(rows - ci, cols - cj) < 10000 / px
print("Slope:")
print(np.nanmean(slope[mask]))

csv_gen()