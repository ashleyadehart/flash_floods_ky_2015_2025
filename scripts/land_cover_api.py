# Landcover API Script
## This script was generated using Google AI. The purpose of this script was to gather geographical data for locations involved in each flash flooding event.

from pathlib import Path
import pandas as pd
from arcgis.gis import GIS
from arcgis.raster import ImageryLayer

# CONFIGURATION & CONSTANTS
INPUT_FILE = Path("data/processed/flash_floods_ky_event_info.csv")
OUTPUT_FILE = Path("data/processed/flash_floods_ky_nlcd_results.csv")

# ARCGIS CONNECTION
API_KEY = "YOUR API KEY GOES HERE"
ARCGIS_URL = "https://www.arcgis.com"

# Living Atlas unique item IDs
NLCD_ID = "32e2ccc6416746a9a72b4d216813f84f"
ELEV_ID = "58a541efc59545e6b7137f961d7de883"
IMPERV_ID = "6df535f263dd44f489365eed49461a38"

# National Land Cover Database (NLCD) Classification Mapping
NLCD_CLASSES = {
    11: "Open Water",
    21: "Developed, Open Space",
    22: "Developed, Low Intensity",
    23: "Developed, Medium Intensity",
    24: "Developed, High Intensity",
    31: "Barren Land",
    41: "Deciduous Forest",
    42: "Evergreen Forest",
    43: "Mixed Forest",
    52: "Shrub/Scrub",
    71: "Grassland/Herbaceous",
    81: "Pasture/Hay",
    82: "Cultivated Crops",
    90: "Woody Wetlands",
    95: "Emergent Herbaceous Wetlands"
}


def initialize_layers(api_key: str) -> tuple:
    """Connects to the ArcGIS GIS API and returns the necessary imagery layers."""
    print("Connecting to ArcGIS Living Atlas layers...")
    gis = GIS(ARCGIS_URL, api_key=api_key)
    
    nlcd_layer = ImageryLayer(gis.content.get(NLCD_ID).url, gis=gis)
    elev_layer = ImageryLayer(gis.content.get(ELEV_ID).url, gis=gis)
    imp_layer = ImageryLayer(gis.content.get(IMPERV_ID).url, gis=gis)
    
    print("All layers connected successfully.")
    return nlcd_layer, elev_layer, imp_layer


def query_layer_value(layer: ImageryLayer, geom: dict):
    """Safely queries an imagery layer geometry point and pulls its pixel value."""
    try:
        response = layer.identify(geometry=geom, return_pixel_values=True)
        return response.get("value", None)
    except Exception as e:
        print(f"Network error while querying layer {layer.url}: {e}")
        return None


def fetch_geospatial_attributes(df: pd.DataFrame, layers: tuple) -> pd.DataFrame:
    """Iterates through rows to query spatial land metrics for coordinate midpoints."""
    nlcd_layer, elev_layer, imp_layer = layers
    
    nlcd_code_list = []
    nlcd_class_list = []
    elevation_list = []
    impervious_list = []

    for idx, row in df.iterrows():
        mid_lat = (row["BEGIN_LAT"] + row["END_LAT"]) / 2
        mid_lon = (row["BEGIN_LON"] + row["END_LON"]) / 2

        if pd.isna(mid_lat) or pd.isna(mid_lon):
            print(f"Warning: Missing coordinates at row index {idx}. Skipping.")
            nlcd_code_list.append(None)
            nlcd_class_list.append(None)
            elevation_list.append(None)
            impervious_list.append(None)
            continue

        # Construct spatial geometry object
        geom = {"x": mid_lon, "y": mid_lat, "spatialReference": {"wkid": 4326}}

        # Safely extract values on an isolated per-query level
        val_nlcd = query_layer_value(nlcd_layer, geom)
        val_elev = query_layer_value(elev_layer, geom)
        val_imp = query_layer_value(imp_layer, geom)

        # Parse and save Land Cover details
        if val_nlcd is not None:
            c_code = int(val_nlcd)
            nlcd_code_list.append(c_code)
            nlcd_class_list.append(NLCD_CLASSES.get(c_code, "Unknown"))
        else:
            nlcd_code_list.append(None)
            nlcd_class_list.append(None)

        # Parse and save Elevation (meters) and Impervious surface metrics
        elevation_list.append(float(val_elev) if val_elev is not None else None)
        impervious_list.append(int(val_imp) if val_imp is not None else None)

        if idx % 100 == 0 and idx > 0:
            print(f"Processed {idx} rows...")

    # Assign lists directly back to dataframe mapping safely
    df["NLCD_CODE"] = nlcd_code_list
    df["NLCD_CLASS"] = nlcd_class_list
    df["ELEVATION_M"] = elevation_list
    df["IMPERVIOUS_SURFACE_PCT"] = impervious_list
    
    return df


if __name__ == "__main__":
    if not INPUT_FILE.is_file():
        print(f"[Error] Source file not found at: {INPUT_FILE.resolve()}")
        print("Please verify your current working directory and path structure.")
    elif API_KEY == "YOUR API KEY GOES HERE":
        print("[Error] Please substitute your actual ArcGIS API_KEY string above.")
    else:
        # Load datasets
        flash_flood_df = pd.read_csv(INPUT_FILE)
        
        # Connect and retrieve layers
        atlas_layers = initialize_layers(API_KEY)
        
        # Enrich dataset rows
        processed_df = fetch_geospatial_attributes(flash_flood_df, atlas_layers)
        
        # Save modifications cleanly
        processed_df.to_csv(OUTPUT_FILE, index=False)
        print(f"\nDONE. Cleaned extraction saved to: {OUTPUT_FILE}")
