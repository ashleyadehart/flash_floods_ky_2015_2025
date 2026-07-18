# Landcover API Script 
## This script was generated using Claude Code. 
## The purpose of this code is to gather geographical data for locations involved in each flash flooding event.

import os
from pathlib import Path
import pandas as pd
from arcgis.gis import GIS
from arcgis.raster import ImageryLayer
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
 
load_dotenv()  # reads variables from a .env file in the current directory into the environment
 
# CONFIGURATION & CONSTANTS
ARCGIS_URL = "https://arcgis.com"
 
LAYER_IDS = {
    "nlcd": "32e2ccc6416746a9a72b4d216813f84f",
    "elev": "58a541efc59545e6b7137f961d7de883",
    "imperv": "6df535f263dd44f489365eed49461a38",
}
 
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
    95: "Emergent Herbaceous Wetlands",
}
 
 
def initialize_layers(api_key: str) -> tuple:
    """Connects to the ArcGIS GIS API with strict SSL validation and returns the three imagery layers."""
    print("Connecting to ArcGIS Living Atlas layers...")
    gis = GIS(ARCGIS_URL, api_key=api_key, verify_cert=True)
 
    layers = {
        name: ImageryLayer(gis.content.get(item_id).url, gis=gis)
        for name, item_id in LAYER_IDS.items()
    }
    print("All layers connected successfully.")
    return layers["nlcd"], layers["elev"], layers["imperv"]
 
 
def query_layer_value(layer: ImageryLayer, geom: dict):
    """Queries an imagery layer at a point geometry and returns its pixel value, or None on failure."""
    try:
        response = layer.identify(geometry=geom, return_pixel_values=True)
        return response.get("value", None)
    except Exception:
        return None
 
 
def process_single_row(idx, row, layers):
    """Worker function to process a single row's spatial variables concurrently."""
    nlcd_layer, elev_layer, imp_layer = layers
 
    mid_lat = (row["begin_lat"] + row["end_lat"]) / 2
    mid_lon = (row["begin_lon"] + row["end_lon"]) / 2
 
    if pd.isna(mid_lat) or pd.isna(mid_lon):
        return idx, (None, None, None, None)
 
    geom = {"x": mid_lon, "y": mid_lat, "spatialReference": {"wkid": 4326}}
 
    val_nlcd = query_layer_value(nlcd_layer, geom)
    val_elev = query_layer_value(elev_layer, geom)
    val_imp = query_layer_value(imp_layer, geom)
 
    c_code = int(val_nlcd) if val_nlcd is not None else None
    c_class = NLCD_CLASSES.get(c_code, "Unknown") if c_code is not None else None
    elevation = float(val_elev) if val_elev is not None else None
    impervious = int(val_imp) if val_imp is not None else None
 
    return idx, (c_code, c_class, elevation, impervious)
 
 
def fetch_geospatial_attributes(
    df: pd.DataFrame,
    layers: tuple,
    max_workers: int = 20,
    checkpoint_every: int = 50,
    checkpoint_file: Path = None,
) -> pd.DataFrame:
    """Uses a thread pool to concurrently fetch metrics for all rows and joins them onto the dataframe.
 
    If checkpoint_file is provided, partial results are written to disk every
    `checkpoint_every` completed rows so progress isn't lost on a crash or interruption.
    """
    print(f"Starting batch execution using {max_workers} concurrent threads...")
 
    cols = ["nlcd_code", "nlcd_class", "elevation_m", "impervious_surface_pct"]
    results = {}
    total_rows = len(df)
 
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(process_single_row, idx, row, layers): idx
            for idx, row in df.iterrows()
        }
 
        for completed, future in enumerate(as_completed(futures), 1):
            idx, values = future.result()
            results[idx] = values
 
            if completed % 100 == 0 or completed == total_rows:
                print(f"Progress: {completed}/{total_rows} rows extracted ({completed/total_rows*100:.1f}%)")
 
            if checkpoint_file is not None and completed % checkpoint_every == 0:
                partial_result_df = pd.DataFrame.from_dict(results, orient="index", columns=cols)
                df.join(partial_result_df).to_csv(checkpoint_file, index=False)
                print(f"Checkpoint saved at {completed}/{total_rows} rows -> {checkpoint_file}")
 
    result_df = pd.DataFrame.from_dict(results, orient="index", columns=cols)
    return df.join(result_df)
 
 
def main():
    # Execution configurations
    API_KEY = os.environ.get("ARCGIS_API_KEY")
    INPUT_FILE = Path("data/processed/flash_floods_ky_event_info.csv")
    OUTPUT_FILE = Path("data/processed/flash_floods_ky_nlcd_data.csv")
 
    # Pre-execution environment checks
    if not INPUT_FILE.is_file():
        print(f"[Error] Source file not found at: {INPUT_FILE.resolve()}")
        return
    if not API_KEY:
        print("[Error] Set the ARCGIS_API_KEY environment variable before running.")
        return
 
    # Load datasets
    flash_flood_df = pd.read_csv(INPUT_FILE)
 
    # Connect and retrieve layers
    atlas_layers = initialize_layers(API_KEY)
 
    # Enrich dataset rows concurrently, checkpointing to OUTPUT_FILE every 50 rows
    processed_df = fetch_geospatial_attributes(
        flash_flood_df,
        atlas_layers,
        max_workers=25,
        checkpoint_every=50,
        checkpoint_file=OUTPUT_FILE,
    )
 
    # Save results
    processed_df.to_csv(OUTPUT_FILE, index=False)
    print(f"\nDONE. Cleaned extraction saved to: {OUTPUT_FILE}")
 
 
if __name__ == "__main__":
    main()