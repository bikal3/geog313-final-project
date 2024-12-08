import ee
import geemap
import pandas as pd
from datetime import datetime
#-------------------------------------------------------------------------------------------------------------------
def initialize_gee():
    """
    Authenticate and initialize the Google Earth Engine API.
    """
    try:
        ee.Initialize()
        print("Google Earth Engine initialized successfully.")
    except Exception as e:
        print("Authentication required. Proceeding to authenticate...")
        ee.Authenticate()
        ee.Initialize()
        print("Google Earth Engine authenticated and initialized successfully.")

#-------------------------------------------------------------------------------------------------------------------
def date_to_unix(date_str):
    """
    Convert a date string in 'YYYY-MM-DD' format to Unix timestamp in milliseconds.

    Parameters:
    - date_str (str): The date string to convert.

    Returns:
    - int: Unix timestamp in milliseconds.
    """
    return int(datetime.strptime(date_str, '%Y-%m-%d').timestamp() * 1000)
#-------------------------------------------------------------------------------------------------------------------
def display_mtbs_burn_severity(start_date, end_date, bbox):
    """
    Display the MTBS burn severity map within a specified date range and bounding box.

    Parameters:
    - start_date (str): The start date in 'YYYY-MM-DD' format.
    - end_date (str): The end date in 'YYYY-MM-DD' format.
    - bbox (list): Bounding box as [min_lon, min_lat, max_lon, max_lat].
    """

    # Load the MTBS burn severity dataset
    mtbs = ee.ImageCollection("USFS/GTAC/MTBS/annual_burn_severity_mosaics/v1")

    # Filter the dataset by the specified date range
    mtbs_filtered = mtbs.filterDate(start_date, end_date)

    # Define the AOI using the provided bbox
    aoi = ee.Geometry.Rectangle(bbox)

    # Define visualization parameters
    vis_params = {
        'bands': ['Severity'],
        'min': 1,
        'max': 4,
        'palette': ['white', 'green', 'yellow', 'red']  # Colors for unburned, low, moderate, and high severity
    }

    # Create a map centered on the AOI
    center_lat = (bbox[1] + bbox[3]) / 2
    center_lon = (bbox[0] + bbox[2]) / 2
    map_ = geemap.Map(center=[center_lat, center_lon], zoom=6)

    # Add the filtered burn severity layer to the map
    map_.addLayer(mtbs_filtered.median().clip(aoi), vis_params, f"MTBS Burn Severity {start_date} to {end_date}")

    # Add the AOI boundary to the map
    map_.addLayer(aoi, {'color': 'blue'}, "AOI")

    # Define legend details based on the class table
    legend_dict = {
        'Background': '#000000',
        'Unburned to Low': '#006400',
        'Low': '#7fffd4',
        'Moderate': '#ffff00',
        'High': '#ff0000',
        'Increased Greenness': '#7fff00',
        'Non-Mapping Area': '#ffffff'
    }

    # Add the legend to the map
    map_.add_legend(title="MTBS Burn Severity Legend", legend_dict=legend_dict)

    # Display the map
    return map_
#-------------------------------------------------------------------------------------------------------------------

def display_mtbs_boundaries(bbox, start_date,end_date):
    """
    Display the MTBS burned area boundaries within a specified bounding box and date range.

    Parameters:
    - bbox (list): Bounding box as [min_lon, min_lat, max_lon, max_lat].
    - start_date (str): The start date in 'YYYY-MM-DD' format (default is '2016-01-01').
    - end_date (str): The end date in 'YYYY-MM-DD' format (default is '2021-12-31').
    """
    # Convert start_date and end_date to Unix timestamps in milliseconds
    start_Ig_date = date_to_unix(start_date)
    end_Ig_date = date_to_unix(end_date)

    # Load the MTBS burned area boundaries dataset
    mtbs_boundaries = ee.FeatureCollection('USFS/GTAC/MTBS/burned_area_boundaries/v1')

    # Define the AOI using the provided bbox
    aoi = ee.Geometry.Rectangle(bbox)

    # # Filter the dataset by AOI
    # mtbs_boundaries_filtered = mtbs_boundaries.filterBounds(aoi)

        # Filter the dataset by AOI and Ig_Date range
    mtbs_boundaries_filtered = mtbs_boundaries.filterBounds(aoi).filter(
        ee.Filter.rangeContains('Ig_Date', start_Ig_date, end_Ig_date)
    )

    # Visualization parameters
    vis_params = {
        'fillColor': '#ff8a50',  # Fill color
        'color': '#ff5722',      # Outline color
        'width': 1.0             # Outline width
    }

    # Create a map centered on the AOI
    center_lat = (bbox[1] + bbox[3]) / 2
    center_lon = (bbox[0] + bbox[2]) / 2
    map_ = geemap.Map(center=[center_lat, center_lon], zoom=6)

    # Add the filtered burned area boundaries layer to the map
    map_.addLayer(mtbs_boundaries_filtered, vis_params, f"MTBS Burned Area Boundaries ({start_date} to {end_date})")

    # Add the AOI boundary to the map for reference
    map_.addLayer(aoi, {'color': 'blue'}, 'AOI Boundary')

    # Display the map
    return map_
#-------------------------------------------------------------------------------------------------------------------
def display_mtbs_by_event_id(event_id):
    """
    Display the MTBS burned area boundary for a specific Event ID.

    Parameters:
    - event_id (str): The Event ID to filter the dataset by.
    """

    # Load the MTBS burned area boundaries dataset
    dataset = ee.FeatureCollection('USFS/GTAC/MTBS/burned_area_boundaries/v1')

    # Define the field and value to filter by
    field_name = 'Event_ID'  # Field name to filter by

    # Filter the dataset by the specified Event ID
    filtered_feature = dataset.filter(ee.Filter.eq(field_name, event_id))

    # Check if the filtered dataset is empty
    count = filtered_feature.size().getInfo()
    if count == 0:
        print(f"No feature found with {field_name}: {event_id}")
        return None
    else:
        print(f"Displaying feature with {field_name}: {event_id}")

    # Visualization parameters
    vis_params = {
        'fillColor': '#ff8a50',  # Fill color for the boundary
        'color': '#ff5722',      # Outline color
        'width': 2.0             # Outline width
    }

    # Create a map object
    map_ = geemap.Map()

    # Add the filtered feature to the map
    map_.addLayer(filtered_feature, vis_params, f"{field_name}: {event_id}")

    # Zoom to the feature if it exists
    map_.centerObject(filtered_feature, zoom=10)

    # Display the map
    return map_
#-------------------------------------------------------------------------------------------------------------------
def get_mtbs_properties(event_id):
    """
    Retrieve the properties of an MTBS burned area boundary feature based on Event ID.

    Parameters:
    - event_id (str): The Event ID to filter the dataset by.

    Returns:
    - pd.DataFrame: A DataFrame containing the feature's properties.
    """
    # Load the MTBS burned area boundaries dataset
    dataset = ee.FeatureCollection('USFS/GTAC/MTBS/burned_area_boundaries/v1')

    # Filter the dataset by the specified Event ID
    filtered_feature = dataset.filter(ee.Filter.eq('Event_ID', event_id)).first()

    # Check if the feature exists
    if filtered_feature is None:
        print(f"No feature found with Event_ID: {event_id}")
        return None
    else:
        # Get the feature's properties
        properties = filtered_feature.getInfo()['properties']

        # Convert the properties dictionary to a DataFrame
        df = pd.DataFrame([properties])

        return df
#-------------------------------------------------------------------------------------------------------------------    
def get_mtbs_time_series_by_Ig_date(bbox, start_date, end_date):
    """
    Perform a time series analysis on the MTBS burned area boundaries dataset using Ig_Date range.

    Parameters:
    - aoi (ee.Geometry): The area of interest.
    - start_Ig_date (int): Start Ig_Date in Unix timestamp (milliseconds).
    - end_Ig_date (int): End Ig_Date in Unix timestamp (milliseconds).

    Returns:
    - pd.DataFrame: DataFrame containing the date and burned area size.
    """
    # Convert start_date and end_date to Unix timestamps in milliseconds
    start_Ig_date = date_to_unix(start_date)
    end_Ig_date = date_to_unix(end_date)
    # Load the MTBS burned area boundaries dataset
    mtbs = ee.FeatureCollection('USFS/GTAC/MTBS/burned_area_boundaries/v1')
    # Define the area of interest (Example: California)
    aoi = ee.Geometry.Rectangle(bbox) 
    
    # Filter the dataset by AOI and Ig_Date range
    mtbs_filtered = mtbs.filterBounds(aoi).filter(
        ee.Filter.rangeContains('Ig_Date', start_Ig_date, end_Ig_date)
    )

    # Function to extract date and burned area size
    def extract_properties(feature):
        return ee.Feature(None, {
            # Convert the Unix timestamp to a date string
            'Date': ee.Date(feature.get('Ig_Date')).format('YYYY-MM-dd'),
            'BurnBndAc': feature.get('BurnBndAc')
        })

    # Map the function over the filtered dataset
    mtbs_mapped = mtbs_filtered.map(extract_properties)

    # Convert the FeatureCollection to a list of dictionaries
    data = mtbs_mapped.getInfo()

    # Extract properties from the list
    features = [feature['properties'] for feature in data['features']]

    # Convert to DataFrame
    df = pd.DataFrame(features)

    # Convert 'Date' to datetime and sort the DataFrame
    if not df.empty:
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values('Date')

    return df

#-------------------------------------------------------------------------------------------------------------------

