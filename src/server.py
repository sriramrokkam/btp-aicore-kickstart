import os
import json
from flask import Flask, jsonify
from srv import *

app = Flask(__name__)

# Load VCAP_SERVICES once at startup and extract service lists
def load_service_lists():
    vcap_env = os.getenv("VCAP_SERVICES")
    vcap_services = None
    if vcap_env:
        try:
            vcap_services = json.loads(vcap_env)
        except Exception:
            vcap_services = None
    if not vcap_services:
        # Try to load from vcap_services.json (lowercase, JSON format)
        vcap_path = os.path.join(os.path.dirname(__file__), '..', 'vcap_services.json')
        if os.path.exists(vcap_path):
            with open(vcap_path, 'r') as f:
                file_json = json.load(f)
                # Accept both {"VCAP_SERVICES": {...}} and {...} at root
                if "VCAP_SERVICES" in file_json:
                    vcap_services = file_json["VCAP_SERVICES"]
                else:
                    vcap_services = file_json
        else:
            # Fallback to VCAP_SERVICES.json (capitalized)
            vcap_path_cap = os.path.join(os.path.dirname(__file__), '..', 'VCAP_SERVICES.json')
            if os.path.exists(vcap_path_cap):
                with open(vcap_path_cap, 'r') as f:
                    file_json = json.load(f)
                    if "VCAP_SERVICES" in file_json:
                        vcap_services = file_json["VCAP_SERVICES"]
                    else:
                        vcap_services = file_json
            else:
                vcap_services = {}
    # Log the raw structure for debugging
    from srv.logger_srv import log_info
    log_info(f"Raw VCAP_SERVICES structure: {json.dumps(vcap_services)[:1000]}")
    # Extract lists for each service
    # Prefer hana_services if present and non-empty, else hana
    hana_entries = vcap_services.get("hana_services")
    if not hana_entries:
        hana_entries = vcap_services.get("hana", [])
    if not hana_entries:
        raise Exception("No HANA service found in VCAP_SERVICES (checked 'hana_services' and 'hana')")
    hana_list = []
    for entry in hana_entries:
        creds = entry.get("credentials", {})
        hana_list.append({
            "user": creds.get("user"),
            "password": creds.get("password"),
            "host": creds.get("host"),
            "port": creds.get("port"),
            "schema": creds.get("schema")
        })
    if not hana_list:
        raise Exception("hana_services must be a non-empty list.")
    xsuaa_entries = vcap_services.get("xsuaa", [])
    xsuaa_list = []
    for entry in xsuaa_entries:
        creds = entry.get("credentials", {})
        xsuaa_list.append({
            "clientid": creds.get("clientid"),
            "clientsecret": creds.get("clientsecret"),
            "url": creds.get("url"),
            "verificationkey": creds.get("verificationkey")
        })
    if not xsuaa_list:
        log_info("No XSUAA service found in VCAP_SERVICES.")
    destination_entries = vcap_services.get("destination", [])
    destination_list = []
    for entry in destination_entries:
        creds = entry.get("credentials", {})
        destination_list.append({
            "clientid": creds.get("clientid"),
            "clientsecret": creds.get("clientsecret"),
            "url": creds.get("url"),
            "uri": creds.get("uri")
        })
    if not destination_list:
        log_info("No Destination service found in VCAP_SERVICES.")
    object_store_entries = vcap_services.get("objectstore", [])
    object_store_list = []
    for entry in object_store_entries:
        creds = entry.get("credentials", {})
        object_store_list.append(creds)
    if not object_store_list:
        log_info("No Object Store service found in VCAP_SERVICES.")
    return hana_list, xsuaa_list, destination_list, object_store_list

from srv.logger_srv import log_info
log_info("Flask app starting up and loading service lists...")
hana_list, xsuaa_list, destination_list, object_store_list = load_service_lists()
log_info("Service lists loaded.")

# Log all credentials lists at startup for debugging
log_info(f"HANA credentials list: {hana_list}")
log_info(f"XSUAA credentials list: {xsuaa_list}")
log_info(f"Destination credentials list: {destination_list}")
log_info(f"Object Store credentials list: {object_store_list}")

@app.route("/health")
def health():
    log_info("/health endpoint called")
    return {"status": "ok"}

@app.route("/hana-user")
def hana_user():
    log_info("/hana-user endpoint called")
    try:
        user = get_hana_user(hana_list)
        log_info(f"/hana-user success: {user}")
        return {"hana_user": user}
    except Exception as e:
        from srv.logger_srv import log_exception
        log_exception("/hana-user error", e)
        return {"error": str(e)}

@app.route("/xsuaa-token")
def xsuaa_token():
    log_info("/xsuaa-token endpoint called")
    try:
        token = get_xsuaa_token(xsuaa_list)
        log_info("/xsuaa-token success")
        return {"xsuaa_token": token}
    except Exception as e:
        from srv.logger_srv import log_exception
        log_exception("/xsuaa-token error", e)
        return {"error": str(e)}

@app.route("/destination-token")
def destination_token():
    log_info("/destination-token endpoint called")
    try:
        token = get_destination_token(destination_list)
        log_info("/destination-token success")
        return {"destination_token": token}
    except Exception as e:
        from srv.logger_srv import log_exception
        log_exception("/destination-token error", e)
        return {"error": str(e)}

@app.route("/object-store-token")
def object_store_token():
    log_info("/object-store-token endpoint called")
    try:
        token = get_object_store_token(object_store_list)
        log_info("/object-store-token success")
        return {"object_store_token": token}
    except Exception as e:
        from srv.logger_srv import log_exception
        log_exception("/object-store-token error", e)
        return {"error": str(e)}

@app.route("/aicore-credentials")
def aicore_credentials():
    log_info("/aicore-credentials endpoint called")
    try:
        from srv.destination_srv import get_aicore_credentials
        creds = get_aicore_credentials(xsuaa_list, destination_list)
        log_info(f"/aicore-credentials result: {creds}")
        # Redact sensitive fields for response
        redacted = {k: ("***REDACTED***" if "secret" in k.lower() or "password" in k.lower() else v) for k, v in creds.items()}
        return jsonify({"status": "success", "aicore_destination": redacted})
    except Exception as e:
        from srv.logger_srv import log_exception
        log_exception("Failed to fetch AI Core credentials via destination", e)
        return jsonify({"status": "error", "error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))