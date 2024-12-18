import os
import dask_geopandas as dg
import geopandas as gpd
import boto3
import leafmap
from botocore.exceptions import ClientError
from dask.distributed import Client, LocalCluster

#-------------------------------------------------------------------------------------------------------------------
def initialize_dask_cluster(**cluster_kwargs):
    """
    Initializes a Dask LocalCluster and Client, and prints the dashboard link.
    
    Parameters:
    - cluster_kwargs: Optional keyword arguments to configure the LocalCluster.
                      Examples: n_workers=4, threads_per_worker=2, memory_limit='2GB'
    
    Returns:
    - client: The initialized Dask Client.
    """
    # Initialize LocalCluster with optional arguments
    cluster = LocalCluster(**cluster_kwargs)
    
    # Create a Dask Client connected to the cluster
    client = Client(cluster)
    
    # Print the dashboard link
    print(f"Dask Dashboard is available at: {client.dashboard_link}")
    
    return client

#-------------------------------------------------------------------------------------------------------------------
def get_s3_keys(bucket_name, prefix, client):
    """
    Fetches all the S3 keys associated with a specified prefix.

    Inputs:
    --------
    bucket_name : string
        The name of the S3 bucket.
    prefix : string
        The prefix to filter the keys (e.g., folder path).
    client : boto3 client object
        An S3 client returned by boto3.client.

    Returns:
    --------
    keys : list
        List of all keys that match the given prefix.
    """
    keys = []    

    response = client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    for obj in response['Contents']:
        keys.append(obj['Key'])

    return keys  
#-------------------------------------------------------------------------------------------------------------------
def get_usgs_data(file_name, s3_client,local_path):

    bucket_name = 'cboettig'
    prefix = "fire/"
    file_prefix = f"{prefix}{file_name}"
    keys = get_s3_keys(bucket_name, file_prefix, s3_client)

    for key in keys:
        local_fname = f"{local_path}/{key.split("/")[-1]}"
        if not os.path.exists(local_fname):
            print(f"File not found locally. Downloading from s3...")
            
            try:
                s3_client.download_file(Bucket = bucket_name,
                                        Key = key,
                                        Filename = f"{local_path}/{key.split("/")[-1]}"
                                       )
                print("Download complete.")
            except:
                print("An error occurred. Download failed")
        else:
            print("File already exists locally. No download needed.")

    usgs_ddf = dg.read_parquet(f"{local_path}/{file_name}*.parquet", gather_spatial_partitions=False)

    return usgs_ddf
#-------------------------------------------------------------------------------------------------------------------
def get_mtbs_shp(file_name, s3_client,local_path):

    bucket_name = 'cboettig'
    prefix = "fire/USGS-MTBS/"
    file_prefix = f"{prefix}{file_name}"
    keys = get_s3_keys(bucket_name, file_prefix, s3_client)

    for key in keys:
        local_fname = f"{local_path}/{key.split("/")[-1]}"
        if not os.path.exists(local_fname):
            print(f"File not found locally. Downloading from s3...")
            
            try:
                s3_client.download_file(Bucket = bucket_name,
                                        Key = key,
                                        Filename = f"{local_path}/{key.split("/")[-1]}"
                                       )
                print("Download complete.")
            except ClientError as error:
                if error.response["Error"]["Code"] == "404":
                    print("The specified key does not exist in the bucket.")
                else:
                    print(f"An error occurred: {error}")
            except Exception as error:
                print(f"An unexpected error occurred: {error}")
        else:
            print("File already exists locally. No download needed.")

    mtbs_shp_ddf = dg.read_file(f"{local_path}/{file_name}.shp",npartitions=4)

    return mtbs_shp_ddf
#-------------------------------------------------------------------------------------------------------------------

def create_wildfire_severity_map(mtbs_shp_ddf):
    """
    Generates a wildfire severity map for the United States based on MTBS data.

    Parameters:
    - mtbs_shp_ddf (Dask GeoDataFrame): Dask GeoDataFrame containing MTBS wildfire perimeter data.

    Returns:
    - leafmap.Map: Interactive map showing wildfire severity by state.
    """
    
    # Filter the data for Wildfire incidents
    wildfire_ddf = mtbs_shp_ddf[mtbs_shp_ddf['Incid_Type'] == 'Wildfire']

    # Extract state abbreviation from the 'Event_ID' (first two characters)
    wildfire_ddf['State'] = wildfire_ddf['Event_ID'].str[:2]

    # Group by 'State' and count the number of wildfires
    wildfires_by_state = wildfire_ddf.groupby('State').size().compute()

    # Convert to a DataFrame for merging
    wildfires_by_state_df = wildfires_by_state.reset_index()
    wildfires_by_state_df.columns = ['State', 'Wildfire Count']

    # Categorize severity levels
    def classify_severity(count):
        if count < 50:
            return 'Low'
        elif 50 <= count < 200:
            return 'Medium'
        else:
            return 'High'

    wildfires_by_state_df['Severity'] = wildfires_by_state_df['Wildfire Count'].apply(classify_severity)

    # Load US states shapefile from Natural Earth
    us_states = gpd.read_file("https://www2.census.gov/geo/tiger/GENZ2021/shp/cb_2021_us_state_20m.zip")

    # Create a column for state abbreviations in the shapefile
    state_abbrev_mapping = {
        'Alaska': 'AK', 'Hawaii': 'HI', 'Alabama': 'AL', 'Arizona': 'AZ', 'Arkansas': 'AR',
        'California': 'CA', 'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'Florida': 'FL',
        'Georgia': 'GA', 'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA', 'Kansas': 'KS',
        'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD', 'Massachusetts': 'MA',
        'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS', 'Missouri': 'MO', 'Montana': 'MT',
        'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH', 'New Jersey': 'NJ', 'New Mexico': 'NM',
        'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH', 'Oklahoma': 'OK',
        'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC',
        'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT',
        'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY'
    }
    us_states['State'] = us_states['NAME'].map(state_abbrev_mapping)

    # Merge the wildfire counts with the US states shapefile
    us_states = us_states.merge(wildfires_by_state_df, on='State', how='left')
    us_states['Wildfire Count'] = us_states['Wildfire Count'].fillna(0)
    us_states['Severity'] = us_states['Severity'].fillna('Low')

    # Define a style callback function for dynamic styling based on severity
    def style_callback(feature):
        severity = feature['properties']['Severity']
        color_map = {
            'Low': '#ffffb2',
            'Medium': '#fd8d3c',
            'High': '#bd0026'
        }
        return {
            "fillColor": color_map.get(severity, '#ffffb2'),
            "color": "black",
            "weight": 1,
            "fillOpacity": 0.7
        }

    # Create a map using leafmap
    m = leafmap.Map(center=[39.8283, -98.5795], zoom=4)
    
    # Add the US states layer with wildfire counts
    m.add_gdf(
        us_states,
        layer_name='Wildfires by State',
        info_mode='on_click',
        style_callback=style_callback,
    )

    # Add a legend
    m.add_legend(
        title="Wildfire Severity by State",
        labels=['Low', 'Medium', 'High'],
        colors=['#ffffb2', '#fd8d3c', '#bd0026']
    )

    return m
#-------------------------------------------------------------------------------------------------------------------