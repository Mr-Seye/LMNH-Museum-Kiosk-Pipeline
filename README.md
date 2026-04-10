---

# Realtime Museum Kiosk Pipeline

This project implements a real-time ETL pipeline that consumes live interaction data from museum kiosks via a Kafka stream and loads it into a PostgreSQL database. The system validates, cleans, and categorises incoming data before persisting it for downstream analysis and visualisation.

---

## Overview

The pipeline subscribes to a Kafka topic containing kiosk interaction events and processes each message individually. Based on its content, each event is classified and inserted into the appropriate database table:

* **Reviews** (ratings from 0 to 4) are stored in the `review` table
* **Incidents** (e.g. help requests or emergencies) are stored in the `incident` table

The project also includes a dashboard layer and infrastructure configuration to support data exploration and deployment.

---

## Project Structure

```plaintext id="u0jv9d"
project-root/
├── dashboard/
│   ├── terraform/
│   │   ├── main.tf
│   │   ├── outputs.tf
│   │   └── variables.tf
│   ├── README.md
│   ├── angela_dashboard.png
│   ├── consumer.py
│   ├── dashboard_wireframe.png
│   ├── producer.py
│   ├── reset_interactions
│   └── rita_dashboard.png
│
├── pipeline/
│   ├── README.md
│   ├── advanced_data_w1_erd.png
│   ├── analysis.ipynb
│   ├── extract.py
│   ├── pipeline.py
│   ├── schema.sql
│   └── test_extract.py
└── requirements.txt
```

---

## Pipeline Execution

Run the real-time pipeline using:

```bash id="nto4j1"
python pipeline/pipeline.py
```

This script:

* Consumes messages from Kafka
* Validates and cleans incoming data
* Inserts records into the appropriate PostgreSQL tables

---

## Dashboard and Data Interaction

The `dashboard/` directory contains components for interacting with and visualising the data, including Kafka producers for generating test data, consumers for processing streams, and supporting infrastructure configuration.

---

## Data Validation

Incoming messages are validated against a defined set of rules:

* Must include `site` and `val` fields
* `site` must be within the range 0–5
* `val` must be between -1 and 4
* `type` must be either 0 or 1 if present
* Timestamp must fall within operating hours (08:45–18:15)

Invalid messages are logged and excluded from processing.

---
