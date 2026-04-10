---

# Dashboard

This component is responsible for consuming data from Kafka brokers, processing incoming messages, and inserting the results into a PostgreSQL database. It acts as the real-time ingestion layer for downstream storage and analysis.

---

## Overview

The dashboard module connects to a Kafka topic containing kiosk interaction events. It processes each message, applies validation and transformation logic, and populates the corresponding database tables for ratings and incident requests.

---

## Setup

### Environment Variables

Create a `.env` file with the following configuration:

```env
## AWS Details ##
AWS_ACCESS_KEY=your-aws-access-key
AWS_SECRET_KEY=your-aws-secret-key
S3_BUCKET=s3-bucket-name

## RDS Details ## 
DB_NAME=database-name
DB_HOST=database-host
DB_USERNAME=database-username
DB_PASSWORD=database-password
DB_PORT=5432

## Kafka Details ##
BOOTSTRAP_SERVERS=kafka-bootstrap
SECURITY_PROTOCOL=SASL_SSL
SASL_MECHANISM=PLAIN

USERNAME=kafka-username
PASSWORD=kafka-password
GROUP_ID=target-group-id-name
AUTO_OFFSET=latest/earliest
TOPIC=kafka-topic-name
```

These variables define access credentials for AWS, database connectivity, and Kafka configuration.

---

## Installation

Install the required dependencies using:

```bash
pip install -r requirements.txt
```

---

## Development

To run the application locally:

1. Ensure all dependencies are installed and environment variables are configured
2. Execute the main pipeline script:

```bash
python pipeline.py
```

If configured correctly and connected to a valid database, the script will consume messages from Kafka and populate the relevant interaction tables.

---

## Deployment

The system is deployed using Terraform and hosted on AWS infrastructure.

### Infrastructure Provisioning

Navigate to the Terraform directory and initialise the configuration:

```bash
terraform init
terraform apply
```

This provisions the required resources, including EC2 and RDS instances.

---

### Application Deployment

1. Transfer project files to the EC2 instance:

```bash
scp -i ~/Desktop/your-key.pem filename ec2-user@PUBLIC_IP:~/target_directory/
```

2. Set up the database schema (locally or from EC2):

```bash
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USERNAME" -d target_database -f schema.sql
```

3. Install required system dependencies on EC2:

```bash
sudo yum install -y python3 python3-pip
sudo yum install -y postgresql15
```

(Optional)

```bash
sudo yum install -y nano
```

4. Install Python dependencies:

```bash
pip3 install -r requirements.txt
```

5. Configure environment variables by creating a `.env` file on the EC2 instance

---

### Running the Application

Start the pipeline as a background process:

```bash
nohup python3 filename.py > output.log 2>&1 &
```

* Use `ps -ef` to locate the running process
* Use `kill -9 <process_id>` to terminate it

---
Examples of the dashboards for each stakeholder:

<img width="2006" height="1250" alt="image" src="https://github.com/user-attachments/assets/d8ad73a9-5df1-4cf8-9a53-2ee61c798216" />

<img width="2014" height="1240" alt="image" src="https://github.com/user-attachments/assets/a80e268b-e0fc-4ad7-8e3b-f2b556965450" />


