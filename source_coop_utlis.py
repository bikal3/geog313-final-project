import os
import dask_geopandas as dg
import geopandas as gpd
import boto3

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
def get_usgs_data(file_name, s3_client):

    bucket_name = 'cboettig'
    prefix = "fire/"
    file_prefix = f"{prefix}{file_name}"
    keys = get_s3_keys(bucket_name, file_prefix, s3_client)

    for key in keys:
        local_fname = f"./data/{key.split("/")[-1]}"
        if not os.path.exists(local_fname):
            print(f"File not found locally. Downloading from s3...")
            
            try:
                s3_client.download_file(Bucket = bucket_name,
                                        Key = key,
                                        Filename = f"./data/{key.split("/")[-1]}"
                                       )
                print("Download complete.")
            except:
                print("An error occurred. Download failed")
        else:
            print("File already exists locally. No download needed.")

    usgs_ddf = dg.read_parquet(f"./data/{file_name}*.parquet", gather_spatial_partitions=False)

    return usgs_ddf
#-------------------------------------------------------------------------------------------------------------------
def get_mtbs_shp(file_name, s3_client):

    bucket_name = 'cboettig'
    prefix = "fire/USGS-MTBS/"
    file_prefix = f"{prefix}{file_name}"
    keys = get_s3_keys(bucket_name, file_prefix, s3_client)

    for key in keys:
        local_fname = f"./data/{key.split("/")[-1]}"
        if not os.path.exists(local_fname):
            print(f"File not found locally. Downloading from s3...")
            
            try:
                s3_client.download_file(Bucket = bucket_name,
                                        Key = key,
                                        Filename = f"./data/{key.split("/")[-1]}"
                                       )
                print("Download complete.")
            except:
                print("An error occurred. Download failed")
        else:
            print("File already exists locally. No download needed.")

    mtbs_shp_ddf = dg.read_file(f"./data/{file_name}",npartitions=4)

    return mtbs_shp_ddf
#-------------------------------------------------------------------------------------------------------------------