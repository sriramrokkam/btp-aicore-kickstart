# SAP BTP Python AI Core Kickstart Template

This template provides a production-ready Python Flask application integrated with SAP BTP services, focusing on AI Core, HANA Cloud, XSUAA, and Destination services. It serves as a foundation for building scalable AI/ML applications on SAP Business Technology Platform.

## ✨ Features

- **Ready-to-use BTP Service Integration:**
  - SAP AI Core connectivity via Destination service
  - HANA Cloud database integration
  - XSUAA authentication
  - Object Store support
- **Developer-Friendly Setup:**
  - Local development support with `vcap_services.json`
  - Comprehensive logging
  - Modular service architecture
- **Production-Ready:**
  - MTA deployment configuration
  - Service binding automation
  - Error handling & logging

## 🚀 Quick Start

### Prerequisites

1. **SAP BTP Account Setup:**
   - SAP BTP Subaccount with Cloud Foundry
   - Entitlements for:
     - SAP AI Core
     - SAP HANA Cloud
     - Authorization & Trust Management (XSUAA)
     - Destination Service
     - Object Store (optional)

2. **Local Development Tools:**
   - Python 3.8+
   - [Cloud Foundry CLI](https://docs.cloudfoundry.org/cf-cli/install-go-cli.html)
   - [MBT Build Tool](https://sap.github.io/cloud-mta-build-tool/)

### Local Development Setup

1. **Clone & Install:**
   ```bash
   git clone <your-repo-url>
   cd <project-folder>
   pip install -r src/requirements.txt
   ```

2. **Configure VCAP_SERVICES:**
   - Create required services in BTP Cockpit
   - Get service credentials:
     ```bash
     cf create-service-key <service-instance> <key-name>
     cf service-key <service-instance> <key-name>
     ```
   - Save as `vcap_services.json` (format):
     ```json
     {
       "hana": [{...}],
       "xsuaa": [{...}],
       "destination": [{...}]
     }
     ```

3. **Run Locally:**
   ```bash
   cd src
   python server.py
   ```

### Available Endpoints

- `GET /health` - Service health check
- `GET /hana-user` - Test HANA connectivity
- `GET /xsuaa-token` - Verify XSUAA setup
- `GET /destination-token` - Test destination service
- `GET /aicore-credentials` - Validate AI Core access

## 📦 Project Structure

```
├── src/
│   ├── server.py          # Flask application & endpoints
│   ├── requirements.txt   # Python dependencies
│   └── srv/
│       ├── hana_srv.py    # HANA service integration
│       ├── xsuaa_srv.py   # Auth service
│       └── ...
├── mta.yaml              # MTA deployment descriptor
└── vcap_services.json    # Local development credentials
```

## 🚢 Deployment

1. **Build MTA Archive:**
   ```bash
   mbt build
   ```

2. **Deploy to Cloud Foundry:**
   ```bash
   cf deploy mta_archives/*.mtar
   ```

3. **Verify Deployment:**
   ```bash
   cf apps
   cf services
   ```

## 🔒 Security Notes

- Store sensitive data in `vcap_services.json` (git-ignored)
- Use environment variables in production
- Follow SAP security best practices
- Regularly rotate service keys

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## 📚 Resources

- [SAP AI Core Documentation](https://help.sap.com/docs/AI_CORE)
- [SAP BTP Developer Guide](https://help.sap.com/docs/btp)
- [Cloud Foundry CLI Guide](https://docs.cloudfoundry.org/cf-cli/)

## 📫 Support

For issues and feature requests, please use the GitHub issue tracker.

---

Happy coding with SAP BTP and AI Core! 🚀
