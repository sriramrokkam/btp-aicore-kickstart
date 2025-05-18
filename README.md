# LangGraph SAP AI Core BTP Python Bootstart Template

This project is a modular Python Flask backend for SAP BTP, integrating SAP HANA Cloud, XSUAA, Destination, and Object Store services, with ready-to-use AI Core connectivity. It is designed as a bootstart template for any SAP BTP Python AI Core application developer.

---

## 🚀 Quick Start

### 1. Clone the Repository
```sh
git clone <your-repo-url>
cd <project-folder>
```

### 2. Prerequisites
- Python 3.8+
- SAP BTP Subaccount with:
  - SAP HANA Cloud
  - XSUAA (Authorization & Trust Management)
  - Destination Service
  - (Optional) Object Store
  - SAP AI Core instance
- [Cloud Foundry CLI](https://docs.cloudfoundry.org/cf-cli/install-go-cli.html)
- [MBT Build Tool](https://sap.github.io/cloud-mta-build-tool/)

### 3. Setup VCAP_SERVICES for Local Development
- Deploy all required services in BTP Cockpit and bind them to your app.
- Run `cf env <your-app-name>` after deployment and copy the `VCAP_SERVICES` JSON block.
- Save it as `vcap_services.json` in the project root for local testing.
- Or set the environment variable:
  ```sh
  export VCAP_SERVICES=$(cat vcap_services.json)
  ```

### 4. Install Python Dependencies
```sh
pip install -r src/requirements.txt
```

### 5. Run the Flask App Locally
```sh
cd src
python server.py
```

---

## 🏗️ Project Structure

- `src/server.py` — Flask entrypoint, all endpoints, service loading, logging
- `src/srv/` — Modular service logic for HANA, XSUAA, Destination, Object Store, logging
- `mta.yaml` — Multi-Target Application descriptor for SAP BTP deployment
- `vcap_services.json` — Local credentials (see above)
- `db/` — (Optional) Database artifacts

---

## 🔑 Service Activation & BTP Setup

### 1. Create and Bind Services
- In BTP Cockpit, create instances for:
  - SAP HANA Cloud (HDI container)
  - XSUAA (plan: application)
  - Destination (plan: lite)
  - (Optional) Object Store
- Bind all services to your app module in the MTA or via Cockpit.

### 2. Create a Destination for AI Core
- Go to **Connectivity > Destinations** in BTP Cockpit.
- Click **New Destination** and enter:
  - **Name:** `aicore`
  - **Type:** HTTP
  - **URL:** `https://<your-aicore-instance-url>`
  - **Proxy Type:** Internet
  - **Authentication:** OAuth2ClientCredentials
  - **Client ID/Secret:** From your AI Core service key
  - **Token Service URL:** From your AI Core service key
  - Add any required additional properties (e.g., `scope`)
- Click **Check Connection** to verify.

### 3. Assign Role Collections for Destination Access
- Go to **Security > Role Collections** in BTP Cockpit.
- Create a new role collection (e.g., `LangGraphDestinationUser`).
- Add the `DestinationService.<instance>_User` role for your Destination instance.
- Assign the role collection to your user (for local dev) or your app's service instance (for production).

### 4. Deploy to SAP BTP Cloud Foundry
```sh
mbt build
cf deploy mta_archives/<your-mtar-file>.mtar
```

---

## 📝 mta.yaml Documentation

- **python module**: Flask backend, binds all services
- **hana**: HDI container for persistence
- **xsuaa**: AuthN/AuthZ
- **destination**: For AI Core and other HTTP destinations
- **object-store**: (Optional) File storage
- **VCAP_SERVICES**: Used for all credential loading (see above)

---

## 🧑‍💻 For Developers
- All endpoints log key events for easy debugging.
- Modular service logic in `src/srv/` for easy extension.
- Use `/aicore-credentials` to test end-to-end AI Core connectivity via Destination.
- See code comments for further extension points.

---

## 📚 References
- [SAP BTP Python Sample](https://github.com/SAP-samples)
- [SAP AI Core Documentation](https://help.sap.com/docs/AI_CORE)
- [SAP BTP Cockpit Guide](https://help.sap.com/docs/btp)

---

## 💡 Tips
- Always keep your `vcap_services.json` up to date after service changes.
- Use BTP Cockpit to manage roles and service bindings.
- For production, never commit secrets or credentials to git.

---

## 🛠️ Troubleshooting
- **403 Forbidden on Destination:** Assign the correct DestinationService role collection.
- **404 Not Found on AI Core:** Check the destination URL and path.
- **Service not found:** Ensure all services are bound and VCAP_SERVICES is correct.

---

Happy building with SAP BTP and Python AI Core!
