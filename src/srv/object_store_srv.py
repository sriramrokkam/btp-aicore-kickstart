import os
import json

def get_object_store_credentials(object_store_services):
    return object_store_services[0].get("credentials", {})

def get_object_store_token(object_store_services):
    """
    Obtain an object store (S3-compatible) token using credentials from the first object store entry.
    Returns a tuple (access_key, secret_key, endpoint_url, bucket_name).
    """
    creds = object_store_services[0]
    access_key = creds.get("access_key_id")
    secret_key = creds.get("secret_access_key")
    endpoint_url = creds.get("endpoint")
    bucket_name = creds.get("bucket")
    if not all([access_key, secret_key, endpoint_url, bucket_name]):
        raise Exception("Missing object store credentials.")
    return access_key, secret_key, endpoint_url, bucket_name
