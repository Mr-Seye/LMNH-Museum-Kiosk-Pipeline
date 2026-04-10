---

# Pipeline

This component is responsible for extracting data files from Amazon S3, consolidating them, and preparing them for insertion into a PostgreSQL database. It acts as a batch ingestion layer, complementing the real-time streaming components of the system.

---

## Overview

The pipeline retrieves CSV files stored in an S3 bucket, downloads them locally, and combines them into a unified dataset. This processed data can then be used to populate database tables or support further analysis.

---

## Setup

### Environment Variables

Create a `.env` file with the following configuration:

```env id="5m7zq7"
AWS_ACCESS_KEY=your-access-key
AWS_SECRET_KEY=your-secret-key
S3_BUCKET=s3-bucket-name
DB_NAME=database-name
DB_HOST=database-host
DB_USERNAME=username
DB_PASSWORD=password
DB_PORT=5432
```

These variables provide access to AWS resources and define the database connection.

---

## Installation

Install the required dependencies using:

```bash id="r4w7xg"
pip install -r requirements.txt
```

---

## Development

To run the pipeline locally:

1. Ensure all dependencies are installed and environment variables are configured
2. Execute the pipeline script:

```bash id="i2x8kq"
python pipeline.py
```

If configured correctly, the script will:

* Download CSV files from the specified S3 bucket
* Combine them into a single dataset
* Prepare the data for insertion into the database

---
