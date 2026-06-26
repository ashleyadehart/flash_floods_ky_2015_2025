# Landcover API Script
## This script was generated using Google AI. The purpose of this script was to gather geographical data for locations involved in each flash flooding event.

import pandas as pd
from arcgis.gis import GIS
from arcgis.raster import ImageryLayer

# =====================================================
# CONFIG
# =====================================================
INPUT_FILE = "data/raw/flash_floods_ky_dates_locations.csv"
OUTPUT_FILE = "data/processed/flash_floods_ky_nlcd_results.csv"

# =====================================================
# ARC GIS API KEY (ADD YOUR KEY HERE)
# =====================================================
API_KEY = "YOUR API KEY GOES HERE"

# =====================================================
# CONNECT & INITIALIZE LAYERS
# =====================================================
gis = GIS("https://www.arcgis.com", api_key=API_KEY)

# Living Atlas unique item IDs
NLCD_ID = "32e2ccc6416746a9a72b4d216813f84f"
ELEV_ID = "58a541efc59545e6b7137f961d7de883"
IMPERV_ID = "6df535f263dd44f489365eed49461a38"

print("Connecting to ArcGIS Living Atlas layers...")
nlcd_layer = ImageryLayer(gis.content.get(NLCD_ID).url, gis=gis)
elev_layer = ImageryLayer(gis.content.get(ELEV_ID).url, gis=gis)
imp_layer = ImageryLayer(gis.content.get(IMPERV_ID).url, gis=gis)
print("All layers connected successfully.")

# =====================================================
# LOAD DATA & STORAGE
# =====================================================
df = pd.read_csv(INPUT_FILE)

nlcd_code_list = []
nlcd_class_list = []
elevation_list = []
impervious_list = []

NLCD_CLASSES = {
    11: "Open Water", 21: "Developed, Open Space", 22: "Developed, Low Intensity",
    23: "Developed, Medium Intensity", 24: "Developed, High Intensity", 31: "Barren Land",
    41: "Deciduous Forest", 42: "Evergreen Forest", 43: "Mixed Forest", 52: "Shrub/Scrub",
    71: "Grassland/Herbaceous", 81: "Pasture/Hay", 82: "Cultivated Crops", 
    90: "Woody Wetlands", 95: "Emergent Herbaceous Wetlands"
}

# =====================================================
# PROCESS ROWS
# =====================================================
for idx, row in df.iterrows():
    try:
        mid_lat = (row["BEGIN_LAT"] + row["END_LAT"]) / 2
        mid_lon = (row["BEGIN_LON"] + row["END_LON"]) / 2
        
        if pd.isna(mid_lat) or pd.isna(mid_lon):
            raise ValueError("Missing coordinate")
            
        geom = {"x": mid_lon, "y": mid_lat, "spatialReference": {"wkid": 4326}}
        
        # 1. Query Land Cover
        res_nlcd = nlcd_layer.identify(geometry=geom, return_pixel_values=True)
        val_nlcd = res_nlcd.get("value", None)
        
        # 2. Query Elevation (Returns meters by default)
        res_elev = elev_layer.identify(geometry=geom, return_pixel_values=True)
        val_elev = res_elev.get("value", None)
        
        # 3. Query Impervious % (Returns continuous 0-100 value)
        res_imp = imp_layer.identify(geometry=geom, return_pixel_values=True)
        val_imp = res_imp.get("value", None)
        
        # Parse & Save Land Cover
        if val_nlcd is not None:
            c_code = int(val_nlcd)
            nlcd_code_list.append(c_code)
            nlcd_class_list.append(NLCD_CLASSES.get(c_code, "Unknown"))
        else:
            nlcd_code_list.append(None)
            nlcd_class_list.append(None)
            
        # Parse & Save Elevation
        elevation_list.append(float(val_elev) if val_elev is not None else None)
        
        # Parse & Save Impervious %
        impervious_list.append(int(val_imp) if val_imp is not None else None)
            
        if idx % 100 == 0:
            print(f"Processed {idx} rows")
            
    except Exception as e:
        print(f"Error row {idx}: {e}")
        nlcd_code_list.append(None)
        nlcd_class_list.append(None)
        elevation_list.append(None)
        impervious_list.append(None)

# =====================================================
# SAVE OUTPUT
# =====================================================
df["NLCD_CODE"] = nlcd_code_list
df["NLCD_CLASS"] = nlcd_class_list
df["ELEVATION_M"] = elevation_list
df["IMPERVIOUS_SURFACE_PCT"] = impervious_list

df.to_csv(OUTPUT_FILE, index=False)
print(f"\nDONE. Saved to: {OUTPUT_FILE}")