<!-- GitHub Copilot Custom Instructions -->

## 📘 Project Summary

This project implements a multi-agent **LangGraph-based AI workflow** integrated with **SAP AI Core**, and deployed on **SAP BTP Cloud Foundry** using **Multi-Target Application (MTA)**. The goal is to build an intelligent chatbot system capable of processing PDFs and images, enriching data via LLMs, and querying structured and unstructured sources like knowledge graphs and SQL tables.

The entire project is developed using **Python**, with workflows orchestrated through **LangGraph**, and version-controlled via a **public GitHub repository**. CI/CD is handled using **GitHub Actions**.

---

## 🎯 Project Objectives

1. Build a **Flask-based Python application** that exposes a chatbot endpoint.
2. Support file uploads (PDF, image) and store the content in **SAP HANA Cloud**.
3. Convert uploaded documents into a **Knowledge Graph** using LangGraph.
4. Use **SAP AI Core APIs** to:
   - Run LLM models.
   - Enrich knowledge graph content.
   - Perform entity recognition and external lookups.

---

## 🧠 LangGraph Tooling (Agent Functions)

Each LangGraph node functions as a "tool" in the agentic workflow:

- **Tool 1**: Query the knowledge graph and return answers.
- **Tool 2**: Use LLMs from SAP AI Core to enrich and augment document data.
- **Tool 3**: Detect organizations and retrieve current stock practices.
- **Tool 4**: Detect places and provide current temperature via weather APIs.
- **Tool 5**: Detect people and fetch current news articles about them.

---

## 🧱 Architecture & Design Principles

- Use **LangGraph** to build agentic workflows in Python.
- Integrate with **SAP AI Core** via REST APIs for inference and job control.
- Persist data (files, metadata, vector embeddings) in **SAP HANA Cloud**.
- Follow Python best practices (modular, type-safe, well-commented).
- Use **RESTful APIs** throughout the project for modular service access.
- Leverage **GitHub** for source control, versioning, and team collaboration.

---

## 🚀 Deployment Strategy

### 🔧 Step 1: Define `mta.yaml` for SAP BTP Cloud Foundry
- Include a `python` module for Flask backend.
- Bind services:
  - `hana` (HDI container)
  - `xsuaa` (auth)
  - Optional: `object-store`, `destination`
- Package and deploy using `mbt build` and `cf deploy`.

### 🔧 Step 2: Read `VCAP_SERVICES` in Python App
- Use the `VCAP_SERVICES` environment variable to dynamically access BTP credentials:
```python
import os, json
vcap_services = json.loads(os.getenv("VCAP_SERVICES", "{}"))
hana_credentials = vcap_services.get("hana", [{}])[0].get("credentials", {})
