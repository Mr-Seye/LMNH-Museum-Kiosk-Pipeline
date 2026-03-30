# Dashboard

Script to pull data from the Kafka Brokers, process them and then populate the database with the data.

## Setup

### Environment variables

The `.env` file should have the following shape:
- `AWS_ACCESS_KEY=`
- `AWS_SECRET_KEY=`
- `S3_BUCKET=`
- `DB_NAME=`
- `DB_HOST=`
- `DB_USERNAME=`
- `DB_PASSWORD=`
- `DB_PORT=5432`
- `BOOTSTRAP_SERVERS=`
- `SECURITY_PROTOCOL=`
- `SASL_MECHANISM=`
- `USERNAME=`
- `PASSWORD=`
- `GROUP_ID=`
- `AUTO_OFFSET=`
- `TOPIC=`

Where the AWS access key, secret keys, database and kafka details are input.

### Installation

- In order to install, simply create an environment with the contents of the `requirements.txt` file

## Development

To run locally, once the required packages are installed:
- Run the pipeline.py file making sure the variables for the buckets are correct, and file paths are also correct.
- Given the steps have been followed correctly and a valid database exists this script should populate the requests and ratings interaction tables with data.

## Deployment

Description of how it will be deployed

- Use `terraform init` while in your terraform directory.
- Then `terraform apply` to build the resources needed for the pipeline, namely the EC2 and RDS and any other variables/secrets needed.
- Now we have to transfer the required files to the EC2 so that it can host the consumer program.
 - We can do this using `scp -i ~/Desktop/your-pemkey.pem filename \ ec2-user@PUBLIC_IP:~/target_directory/`
- Once the files are copied we also need to set up the database in the RDS, we can do this on the EC2 though it is easier to do it locally
 - We can do this using `psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USERNAME" -d target_database -f your_schema_here`
    - You can target an empty database if your schema does not create and connect to a new one
- Now we must connect to our EC2 instance and install any pre-requisites such as python and psql.
    - `sudo yum install -y python3 python3-pip` `sudo yum install -y postgresql15`
    - OPTIONAL (for easier file editing): `sudo yum install -y nano`
- Now we can use `python3 pip install -r requirements.txt`
- Once this is done we must lastly set up the environment variables on the EC2 following the above format by simply making a `.env` file on the EC2 and copying over you local contents.
- Lastly we must launch the program as a background process using `nohum python3 filename.py > filename.out 2>&1 &`
    - Note: either note down the process number output after this is run or use `ps -ef` to locate the process later if you wish to kill it
    - Use `kill -9 process_number` to end the program.
- Now we should have a streaming pipeline that populates data to the database in batches of 100 messages.