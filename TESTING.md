# Testing & Validation Guide: LangGraph SAP AI Core BTP Python Template

This guide helps you verify your project setup and test all key integrations before using this repository as a template for new projects.

---

## 1. Prerequisites Checklist
- [ ] All required SAP BTP services are created and bound (HANA, XSUAA, Destination, Object Store (optional), AI Core)
- [ ] Role collections for Destination access are assigned (see README)
- [ ] `vcap_services.json` is present and up to date for local testing
- [ ] Python 3.8+ and dependencies installed

---

## 2. Local Setup & Smoke Test

### a. Set VCAP_SERVICES
```sh
export VCAP_SERVICES=$(cat vcap_services.json)
```

### b. Install Python Dependencies
```sh
pip install -r src/requirements.txt
```

### c. Start the Flask App
```sh
cd src
python server.py
```

---

## 3. Endpoint Testing

Use `curl` or Postman to test the following endpoints:

### Health Check
```sh
curl http://localhost:8080/health
```
- **Expected:** `{ "status": "ok" }`

### HANA User
```sh
curl http://localhost:8080/hana-user
```
- **Expected:** Returns HANA user info or error

### XSUAA Token
```sh
curl http://localhost:8080/xsuaa-token
```
- **Expected:** Returns a valid XSUAA JWT token

### Destination Token
```sh
curl http://localhost:8080/destination-token
```
- **Expected:** Returns a valid Destination service token

### Object Store Token (if enabled)
```sh
curl http://localhost:8080/object-store-token
```
- **Expected:** Returns a valid Object Store token

### AI Core Credentials & Connectivity
```sh
curl http://localhost:8080/aicore-credentials
```
- **Expected:**
  - Status 200
  - `aicore_destination` object with redacted credentials
  - Health check result from AI Core (status 200 if all is well)
  - If you see 403/404 errors, check role collections and destination config

---

## 4. Common Issues & Fixes

- **403 Forbidden on /aicore-credentials:**
  - Assign the correct DestinationService role collection to your user or app
- **404 Not Found:**
  - Check the destination name and URL in BTP Cockpit
- **Service not found:**
  - Ensure all services are bound and VCAP_SERVICES is correct
- **Token errors:**
  - Check XSUAA and Destination credentials

---

## 5. Ready to Use as Template?
- [ ] All endpoints return expected results
- [ ] No errors in logs
- [ ] README and mta.yaml are up to date
- [ ] .gitignore excludes secrets

If all checks pass, you can now use this repository as a template for new SAP BTP Python AI Core projects!

---

Happy testing!
