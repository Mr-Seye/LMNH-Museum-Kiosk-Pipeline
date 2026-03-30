# Pipeline
## Extract

Script to pull files from the Amazon S3, download them and then combine the `.csv` files into one file.

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

Where the AWS access key, secret keys and database details are input.

### Installation

- In order to install, simply create an environment with the contents of the `requirements.txt` file

## Development

To run locally, once the required packages are installed:
- Run the pipeline.py file making sure the variables for the buckets are correct, and file paths are also correct.
- Given the steps have been followed correctly and a valid database exists this script should populate the requests and ratings interaction tables with data.