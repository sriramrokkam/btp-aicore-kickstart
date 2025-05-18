import os
import json
import hdbcli
from hdbcli import dbapi
from .logger_srv import log_info, log_error, log_exception

def get_hana_user(hana_services):
    # Robustly extract credentials
    log_info("Extracting HANA credentials...")
    if not hana_services or not isinstance(hana_services, list):
        log_error("hana_services must be a non-empty list.")
        raise Exception("hana_services must be a non-empty list.")
    hana_creds = hana_services[0].get("credentials", {}) if "credentials" in hana_services[0] else hana_services[0]
    user = hana_creds.get("user")
    password = hana_creds.get("password")
    host = hana_creds.get("host")
    port = hana_creds.get("port")
    # Validate all required fields
    if not all([user, password, host, port]):
        log_error(f"Missing HANA credentials: user={user}, password={'***' if password else None}, host={host}, port={port}")
        raise Exception(f"Missing HANA credentials: user={user}, password={'***' if password else None}, host={host}, port={port}")
    try:
        log_info(f"Connecting to HANA at {host}:{port} as {user}...")
        conn = dbapi.connect(
            address=host,
            port=int(port),
            user=user,
            password=password,
            encrypt=True,
            sslValidateCertificate=False
        )
        cursor = conn.cursor()
        cursor.execute("SELECT CURRENT_USER FROM DUMMY")
        user = cursor.fetchone()[0]
        log_info(f"Connected to HANA as {user}.")
        cursor.close()
        conn.close()
        return user
    except Exception as e:
        log_exception("Error connecting to HANA or executing query", e)
        raise
