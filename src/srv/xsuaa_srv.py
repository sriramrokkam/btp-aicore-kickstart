"""
xsuaa_utils.py

Utility functions for handling XSUAA OAuth2 token validation, JWT decoding, and outbound token acquisition for SAP BTP applications.
"""
# This file has been moved to src/scripts/xsuaa_srv.py
# Please use the new location for all XSUAA-related utilities.

import os
import json
import requests
import jwt
from flask import request, abort
from functools import wraps
from .logger_srv import log_info, log_error, log_exception

# Get XSUAA credentials from VCAP_SERVICES

def get_xsuaa_credentials(xsuaa_services):
    return xsuaa_services[0].get("credentials", {})

# Validate inbound JWT token from Authorization header

def validate_jwt_token(token, xsuaa_creds=None):
    if xsuaa_creds is None:
        xsuaa_creds = get_xsuaa_credentials()
    public_key = xsuaa_creds.get("verificationkey")
    if not public_key:
        raise Exception("No XSUAA public key found for JWT validation.")
    try:
        decoded = jwt.decode(token, public_key, algorithms=["RS256"], audience=xsuaa_creds.get("xsappname"))
        return decoded
    except Exception as e:
        raise Exception(f"JWT validation failed: {e}")

# Flask decorator for endpoint protection

def require_xsuaa_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            abort(401, description="Missing or invalid Authorization header.")
        token = auth_header.split(" ", 1)[1]
        try:
            user_info = validate_jwt_token(token)
            request.user = user_info
        except Exception as e:
            abort(401, description=str(e))
        return f(*args, **kwargs)
    return decorated

# Outbound token acquisition (client credentials grant)

def get_outbound_jwt_token(xsuaa_creds=None, scopes=None):
    if xsuaa_creds is None:
        xsuaa_creds = get_xsuaa_credentials()
    token_url = xsuaa_creds.get("url") + "/oauth/token"
    client_id = xsuaa_creds.get("clientid")
    client_secret = xsuaa_creds.get("clientsecret")
    payload = {
        "grant_type": "client_credentials"
    }
    if scopes:
        payload["scope"] = scopes
    response = requests.post(
        token_url,
        data=payload,
        auth=(client_id, client_secret),
        headers={"Accept": "application/json"}
    )
    if response.status_code != 200:
        raise Exception(f"Failed to get outbound JWT token: {response.text}")
    return response.json()["access_token"]

def get_xsuaa_token(xsuaa_list):
    # Example: get a token using client credentials from the first xsuaa entry
    creds = xsuaa_list[0]
    # Fix: Ensure no double slashes and missing slash before /oauth/token
    base_url = creds.get("url", "")
    token_url = base_url + "/oauth/token"
    client_id = creds.get("clientid")
    client_secret = creds.get("clientsecret")
    payload = {
        "grant_type": "client_credentials"
    }
    log_info(f"Requesting XSUAA token from {token_url} with client_id={client_id}")
    try:
        response = requests.post(
            token_url,
            data=payload,
            auth=(client_id, client_secret),
            headers={"Accept": "application/json"}
        )
        log_info(f"XSUAA token endpoint response: status={response.status_code}, body={response.text}")
        if response.status_code != 200:
            log_error(f"Failed to get outbound JWT token: {response.text}")
            raise Exception(f"Failed to get outbound JWT token: {response.text}")
        return response.json()["access_token"]
    except Exception as e:
        log_exception("Exception during XSUAA token request", e)
        raise
