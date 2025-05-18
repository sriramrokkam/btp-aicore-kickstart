import os
import json
import requests
from .logger_srv import log_info, log_error, log_exception
from .xsuaa_srv import get_xsuaa_token

def get_destination_credentials(destination_name, xsuaa_list, destination_list):
    """
    Fetch destination credentials (e.g., for AI Core) securely from SAP Destination Service.
    """
    try:
        # Get XSUAA token using the shared function
        access_token = get_xsuaa_token(xsuaa_list)
        dest_service = destination_list[0]
        dest_uri = dest_service.get("uri") or dest_service.get("url")
        if not dest_uri:
            raise Exception("Destination service URI not found in VCAP_SERVICES.")
        dest_uri = dest_uri.rstrip("/") + f"/destination-configuration/v1/destinations/{destination_name}"
        headers = {"Authorization": f"Bearer {access_token}"}
        log_info(f"Fetching destination '{destination_name}' from {dest_uri}")
        resp = requests.get(dest_uri, headers=headers)
        log_info(f"Destination service response: status={resp.status_code}, body={resp.text}")
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        log_exception("Error fetching destination credentials", e)
        raise

def get_aicore_credentials(xsuaa_list, destination_list):
    """
    Fetch AI Core credentials from the destination service (e.g., 'aicore').
    Then, use the destination config to get an OAuth2 token and call /v2/health on the AI Core instance.
    Returns a dict with the health check result and redacted destination config.
    """
    try:
        # 1. Fetch destination config (destination name should match your BTP cockpit, e.g., 'aicore')
        destination_name = "aicore"  # Change if your destination is named differently
        dest_config = get_destination_credentials(destination_name, xsuaa_list, destination_list)
        # 2. Get OAuth2 token for AI Core using destination config
        token_url = dest_config.get("tokenServiceURL")
        client_id = dest_config.get("clientid")
        client_secret = dest_config.get("clientsecret")
        if not all([token_url, client_id, client_secret]):
            raise Exception("Destination config missing OAuth2 properties (tokenServiceURL, clientid, clientsecret)")
        token_resp = requests.post(
            token_url,
            data={"grant_type": "client_credentials"},
            auth=(client_id, client_secret),
            headers={"Accept": "application/json"}
        )
        if token_resp.status_code != 200:
            raise Exception(f"Failed to get AI Core OAuth2 token: {token_resp.text}")
        access_token = token_resp.json()["access_token"]
        # 3. Call /v2/health on the AI Core instance
        base_url = dest_config.get("URL") or dest_config.get("url")
        if not base_url:
            raise Exception("Destination config missing URL property")
        health_url = base_url.rstrip("/") + "/v2/health"
        health_resp = requests.get(health_url, headers={"Authorization": f"Bearer {access_token}"})
        # Redact sensitive fields for response
        redacted = {k: ("***REDACTED***" if "secret" in k.lower() or "password" in k.lower() else v) for k, v in dest_config.items()}
        return {
            "status": "success" if health_resp.status_code == 200 else "error",
            "aicore_health_status": health_resp.status_code,
            "aicore_health_response": health_resp.text,
            "aicore_destination": redacted
        }
    except Exception as e:
        log_exception("Error in get_aicore_credentials", e)
        return {"status": "error", "error": str(e)}

def get_destination_token(destination_services):
    """
    Obtain a destination service token using client credentials from the first destination entry.
    Improved logging for debugging.
    """
    creds = destination_services[0]
    token_url = creds.get("url", "") + "/oauth/token"
    client_id = creds.get("clientid")
    client_secret = creds.get("clientsecret")
    payload = {
        "grant_type": "client_credentials"
    }
    from .logger_srv import log_info, log_error
    log_info(f"Requesting destination token from: {token_url}")
    log_info(f"Using client_id: {client_id}")
    try:
        response = requests.post(
            token_url,
            data=payload,
            auth=(client_id, client_secret),
            headers={"Accept": "application/json"}
        )
        log_info(f"Destination token endpoint response: status={response.status_code}, body={response.text}")
        if response.status_code != 200:
            log_error(f"Failed to get destination token: {response.text}")
            raise Exception(f"Failed to get destination token: {response.text}")
        return response.json()["access_token"]
    except Exception as e:
        log_error(f"Exception during destination token request: {str(e)}")
        raise
