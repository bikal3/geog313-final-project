import ee
import geemap
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import calendar
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
def get_month_start_end(event_date):
    """
    Given an event date, return the start date and end date of that month.

    Parameters:
    - event_date (str): Date string in 'YYYY-MM-DD HH:MM:SS' format.

    Returns:
    - tuple: (start_date, end_date) in 'YYYY-MM-DD' format.
    """
    # Convert event_date to a datetime object
    event_date_dt = datetime.strptime(event_date, '%Y-%m-%d %H:%M:%S')
    
    # Get the first day of the month
    start_date = event_date_dt.replace(day=1).strftime('%Y-%m-%d')
    
    # Get the last day of the month
    last_day = calendar.monthrange(event_date_dt.year, event_date_dt.month)[1]
    end_date = event_date_dt.replace(day=last_day).strftime('%Y-%m-%d')
    
    return start_date, end_date
#-------------------------------------------------------------------------------------------------------------------
from datetime import datetime, timedelta

def get_event_start_end(event_date):
    """
    Given an event date, return the start date as 10 days before the event date 
    and the end date as 10 days after the event date.

    Parameters:
    - event_date (str): Date string in 'YYYY-MM-DD HH:MM:SS' format.

    Returns:
    - tuple: (start_date, end_date) in 'YYYY-MM-DD' format.
    """
    # Convert event_date to a datetime object
    event_date_dt = datetime.strptime(event_date, '%Y-%m-%d %H:%M:%S')
    
    # Calculate the start date as 10 days before the event date
    start_date = (event_date_dt - timedelta(days=10)).strftime('%Y-%m-%d')
    
    # Calculate the end date as 10 days after the event date
    end_date = (event_date_dt + timedelta(days=10)).strftime('%Y-%m-%d')
    
    return start_date, end_date
#-------------------------------------------------------------------------------------------------------------------
def datetime_to_unix(date_str):
    """
    Convert a date string in 'YYYY-MM-DD' format to Unix timestamp in milliseconds.

    Parameters:
    - date_str (str): The date string to convert.

    Returns:
    - int: Unix timestamp in milliseconds.
    """
    return int(datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S' ).timestamp() * 1000)

#-------------------------------------------------------------------------------------------------------------------
def date_to_unix(date_str):
    """
    Convert a date string in 'YYYY-MM-DD' format to Unix timestamp in milliseconds.

    Parameters:
    - date_str (str): The date string to convert.

    Returns:
    - int: Unix timestamp in milliseconds.
    """
    return int(datetime.strptime(date_str, '%Y-%m-%d' ).timestamp() * 1000)

#-------------------------------------------------------------------------------------------------------------------
def unix_to_date(unix_timestamp):
    """
    Convert a Unix timestamp in milliseconds to a date string in 'YYYY-MM-DD HH:MM:SS' format.

    Parameters:
    - unix_timestamp (int): The Unix timestamp in milliseconds to convert.

    Returns:
    - str: Date string in 'YYYY-MM-DD HH:MM:SS' format.
    """
    return datetime.utcfromtimestamp(unix_timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')
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

#----------------------------------------------------------------------------------------------------------
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
def get_mtbs_properties_by_name(event_name):
    """
    Retrieve the properties of an MTBS burned area boundary feature based on Event ID.

    Parameters:
    - event_name (str): The Event ID to filter the dataset by.

    Returns:
    - pd.DataFrame: A DataFrame containing the feature's properties.
    """
    # Load the MTBS burned area boundaries dataset
    dataset = ee.FeatureCollection('USFS/GTAC/MTBS/burned_area_boundaries/v1')

    # Filter the dataset by the specified Event ID
    filtered_feature = dataset.filter(ee.Filter.eq('Incid_Name', event_name)).first()

    # Check if the feature exists
    if filtered_feature is None:
        print(f"No feature found with Incid_Name: {event_name}")
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
def get_season(month):
    """Returns the season for a given month."""
    if month in [12, 1, 2]:
        return 'Winter'
    elif month in [3, 4, 5]:
        return 'Spring'
    elif month in [6, 7, 8]:
        return 'Summer'
    else:
        return 'Autumn'
#-------------------------------------------------------------------------------------------------------------------
# Function to plot BurnBndAc by seasonality
def plot_burned_area_by_season(df):
    if df.empty:
        print("No data available to plot.")
        return

    # Add Year and Season columns
    df['Year'] = df['Date'].dt.year
    df['Season'] = df['Date'].dt.month.apply(get_season)

    # Group by Year and Season and sum the burned area
    season_summary = df.groupby(['Year', 'Season'])['BurnBndAc'].sum().reset_index()

    # Pivot for easier plotting
    pivot_df = season_summary.pivot(index='Year', columns='Season', values='BurnBndAc').fillna(0)

    # Plot the data
    pivot_df.plot(kind='bar', stacked=True, figsize=(12, 7))
    plt.title('Burned Area (BurnBndAc) by Season')
    plt.xlabel('Year')
    plt.ylabel('Burned Area (Acres)')
    plt.legend(title='Season')
    plt.tight_layout()
    plt.show()
#-------------------------------------------------------------------------------------------------------------------
# Function to plot BurnBndAc by seasonality with side-by-side bars
def plot_burned_area_by_season_side(df):
    if df.empty:
        print("No data available to plot.")
        return

    # Add Year and Season columns
    df['Year'] = df['Date'].dt.year
    df['Season'] = df['Date'].dt.month.apply(get_season)

    # Group by Year and Season and sum the burned area
    season_summary = df.groupby(['Year', 'Season'])['BurnBndAc'].sum().reset_index()

    # Pivot for easier plotting
    pivot_df = season_summary.pivot(index='Year', columns='Season', values='BurnBndAc').fillna(0)

    # Plot side-by-side bars
    pivot_df.plot(kind='bar', figsize=(12, 7), width=0.8)
    plt.title('Burned Area (BurnBndAc) by Season')
    plt.xlabel('Year')
    plt.ylabel('Burned Area (Acres)')
    plt.legend(title='Season')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
#-------------------------------------------------------------------------------------------------------------------
# Function to plot BurnBndHa_1000 by seasonality with side-by-side bars
def plot_burned_area_by_season_hectars(df):
    if df.empty:
        print("No data available to plot.")
        return
    # Convert BurnBndAc from acres to hectares and then to ha/1000
    df['BurnBndHa'] = (df['BurnBndAc'] * 0.404686) / 1000
    df.rename(columns={'BurnBndHa': 'BurnBndHa_1000'}, inplace=True)

    # Add Year and Season columns
    df['Year'] = df['Date'].dt.year
    df['Season'] = df['Date'].dt.month.apply(get_season)

    # Group by Year and Season and sum the burned area
    season_summary = df.groupby(['Year', 'Season'])['BurnBndHa_1000'].sum().reset_index()

    # Pivot for easier plotting
    pivot_df = season_summary.pivot(index='Year', columns='Season', values='BurnBndHa_1000').fillna(0)

    # Plot side-by-side bars
    pivot_df.plot(kind='bar', figsize=(12, 7), width=0.8)
    plt.title('Burned Area (ha/1000) by Season')
    plt.xlabel('Year')
    plt.ylabel('Burned Area (Thousands of Hectares)')
    plt.legend(title='Season')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
#-------------------------------------------------------------------------------------------------------------------

def display_mtbs_by_event_start_date(event_name,start_date):
    """
    Display the MTBS burned area boundary for a specific Event ID and Event Date.

    Parameters:
    - event_name (str): The Event ID to filter the dataset by.
    - start_date (str): The Event Date to filter the dataset by (format: 'YYYY-MM-DD').
    """

    # Load the MTBS burned area boundaries dataset
    dataset = ee.FeatureCollection('USFS/GTAC/MTBS/burned_area_boundaries/v1')
    start_Ig_date = datetime_to_unix(start_date)
    # Define the field names for filtering
    field_event_name = 'Incid_Name'      # Field name for Event ID
    field_start_date = 'Ig_Date'  # Field name for Event Date (ensure this matches the dataset's field name)

    # Filter the dataset by the specified Event ID and Event Date
    filtered_feature = dataset.filter(
        ee.Filter.Or(
            ee.Filter.eq(field_event_name, event_name),
            ee.Filter.eq(field_start_date, start_Ig_date)
        )
    )

    # Check if the filtered dataset is empty
    count = filtered_feature.size().getInfo()
    if count == 0:
        print(f"No feature found with {field_event_name}: {event_name} and {field_start_date}: {start_Ig_date}")
        return None
    else:
        print(f"Displaying feature with {field_event_name}: {event_name} and {field_start_date}: {start_Ig_date}")

    # Visualization parameters
    vis_params = {
        'fillColor': '#ff8a50',  # Fill color for the boundary
        'color': '#ff5722',      # Outline color
        'width': 2.0             # Outline width
    }

    # Create a map object
    map_ = geemap.Map()

    # Add the filtered feature to the map
    map_.addLayer(filtered_feature, vis_params, f"{field_event_name}: {event_name}, {field_start_date}: {start_Ig_date}")

    # Zoom to the feature if it exists
    map_.centerObject(filtered_feature, zoom=10)

    # Display the map
    return map_
