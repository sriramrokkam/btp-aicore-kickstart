import os
import json
import requests
from .logger_srv import log_info, log_error, log_exception
from .xsuaa_srv import get_xsuaa_token

def get_destination_token(destination_services):
    """
    Obtain a destination service token using client credentials from the first destination entry.
    """
    if not destination_services:
        raise Exception("No destination credentials found")

    creds = destination_services[0]
    token_url = creds.get("url", "") + "/oauth/token"
    client_id = creds.get("clientid")
    client_secret = creds.get("clientsecret")
    
    if not all([token_url, client_id, client_secret]):
        raise Exception("Missing required destination service credentials")

    payload = {
        "grant_type": "client_credentials"
    }
    
    log_info(f"Requesting destination token from: {token_url}")
    
    try:
        response = requests.post(
            token_url,
            data=payload,
            auth=(client_id, client_secret),
            headers={"Accept": "application/json"}
        )
        log_info(f"Destination token response status: {response.status_code}")
        
        if response.status_code != 200:
            log_error(f"Failed to get destination token: {response.text}")
            raise Exception(f"Failed to get destination token: {response.text}")
            
        return response.json()["access_token"]
    except Exception as e:
        log_error(f"Exception during destination token request: {str(e)}")
        raise

def get_destination_configuration(destination_name, xsuaa_token, destination_list):
    """
    Get configuration for a specific destination.
    """
    if not destination_list:
        raise Exception("No destination credentials found")
        
    dest_creds = destination_list[0]
    dest_base_url = dest_creds.get('uri', dest_creds.get('url'))
    
    if not dest_base_url:
        raise Exception("No destination service URL found")
        
    dest_url = f"{dest_base_url.rstrip('/')}/destination-configuration/v1/destinations/{destination_name}"
    log_info(f"Fetching destination '{destination_name}' from: {dest_url}")
    
    headers = {
        'Authorization': f"Bearer {xsuaa_token}",
        'Content-Type': 'application/json'
    }
    
    response = requests.get(dest_url, headers=headers)
    log_info(f"Destination configuration response status: {response.status_code}")
    
    if response.status_code != 200:
        log_error(f"Failed to get destination configuration: {response.text}")
        raise Exception(f"Failed to get destination configuration: {response.text}")
        
    return response.json()

def get_aicore_credentials(xsuaa_list, destination_list):
    """
    Get AI Core credentials via destination service with OAuth2 client credentials.
    """
    try:
        # Get XSUAA token for destination service access
        xsuaa_token = get_xsuaa_token(xsuaa_list)
        if not xsuaa_token:
            raise Exception("Failed to get XSUAA token")
            
        # Get AI Core destination configuration
        dest_config = get_destination_configuration('aicore', xsuaa_token, destination_list)
        log_info("Successfully retrieved AI Core destination configuration")
        
        # Extract AI Core specific configuration
        aicore_url = dest_config.get('destinationConfiguration', {}).get('URL')
        auth_type = dest_config.get('destinationConfiguration', {}).get('Authentication')
        
        if not aicore_url:
            raise Exception("AI Core URL not found in destination configuration")
            
        if auth_type != 'OAuth2ClientCredentials':
            raise Exception(f"Unexpected authentication type: {auth_type}")
            
        # Get OAuth token for AI Core access
        auth_tokens = dest_config.get('authTokens', [])
        if not auth_tokens:
            raise Exception("No auth tokens found in destination configuration")
            
        access_token = auth_tokens[0].get('value')
        if not access_token:
            raise Exception("No access token found in auth tokens")
            
        # Return the AI Core credentials
        credentials = {
            'url': aicore_url.rstrip('/'),  # Ensure no trailing slash
            'token': access_token,
            'auth_type': auth_type
        }
        
        log_info("Successfully constructed AI Core credentials")
        return credentials
        
    except Exception as e:
        log_exception("Error getting AI Core credentials", e)
        raise e
