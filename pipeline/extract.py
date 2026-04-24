"""Script to install things from the S3 instance."""

# Imports

from os import environ as ENV, _Environ, mkdir, listdir, path
from os.path import exists, join, dirname

from dotenv import load_dotenv
from boto3 import client
import csv
import logging

logger = logging.getLogger(__name__)


def configure_logging(level=logging.INFO) -> None:
    """Configure console logging for the application"""
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )


def get_s3_client(config: _Environ) -> client:
    """Returns S3 client instance."""

    return client(
        service_name="s3",
        aws_access_key_id=config["AWS_ACCESS_KEY"],
        aws_secret_access_key=config["AWS_SECRET_KEY"]
    )


def list_buckets(s3_client: client) -> list[str]:
    """Returns a list of buckets user can access."""
    res = s3_client.list_buckets()

    buckets = res.get("Buckets", [])
    names = [b["Name"] for b in buckets]
    logger.info("Found %d accessible bucket(s).", len(names))
    return names


def choose_bucket(s3_client: client, config: _Environ):
    """Uses bucket provided in .env, otherwise selects the first available bucket."""

    bucket = config.get("S3_BUCKET")

    if bucket:
        logger.info("Using bucket from environment: %s", bucket)
        return bucket

    buckets = list_buckets(s3_client)
    if not buckets:
        logger.error(
            "No accessible S3 buckets found and/or S3_BUCKET is not set.")
        raise RuntimeError(
            "No accessible S3 buckets found and/or S3_BUCKET not set.")
    logger.info("No S3_BUCKET set; defaulting to first bucket: %s", buckets[0])
    return buckets[0]


def list_objects(s3_client: client, bucket_name: str) -> list[str]:
    """Returns a list of objects from a specified bucket."""
    try:
        res = s3_client.list_objects(Bucket=bucket_name)
    except Exception:
        logger.exception("Failed to list objects in bucket: %s", bucket_name)
        raise

    contents = res.get("Contents", [])
    keys = [obj["Key"] for obj in contents]
    logger.info("Listed %d object(s) in bucket '%s'.", len(keys), bucket_name)

    return keys


def validate_parent_dir(filepath: path) -> None:
    """Checks to see if file path exists before creating one"""
    parent = dirname(filepath)
    if parent and not exists(parent):
        parts = parent.split("/")
        current = ""
        for part in parts:
            current = part if current == "" else f"{current}/{part}"
            if current and not exists(current):
                mkdir(current)
                logger.debug("Created directory: %s", current)


def download_objects(s3_client: client, bucket_name: str, keys: list[str], output_dir: path) -> None:
    """Downloads objects in the selected bucket"""
    if not keys:
        logger.warning("No objects to download from bucket '%s'.", bucket_name)
        return

    logger.info("Starting download of %d file(s) to '%s'.",
                len(keys), output_dir)

    failures = 0

    for i, key in enumerate(keys, start=1):
        local_path = join(output_dir, key)
        try:
            validate_parent_dir(local_path)
            s3_client.download_file(
                Bucket=bucket_name,
                Key=key,
                Filename=local_path
            )
            logger.info("Downloaded (%d/%d): %s", i, len(keys), key)
        except Exception:
            failures += 1
            logger.exception(
                "Failed to download key '%s' to '%s'.", key, local_path)

    if failures == 0:
        logger.info("All files downloaded successfully (%d/%d).",
                    len(keys), len(keys))

    else:
        logger.warning(
            "Download finished with %d failure(s). Successful: %d/%d.",
            failures, len(keys) - failures, len(keys)
        )


def extract_csv(keys: list[str]) -> list[str]:
    """Returns a list of .csv files matching the naming convention"""
    targets = [k for k in keys if k.startswith(
        "lmnh_hist_data_") and k.endswith(".csv")]
    logger.info("Identified %d historical CSV file(s).", len(targets))
    return targets


def extract_json(keys: list[str]) -> list[str]:
    """Returns a list of .json files matching the naming convention"""
    targets = [k for k in keys if k.startswith(
        "lmnh_exhibition_") and k.endswith(".json")]
    logger.info("Identified %d exhibition JSON file(s).", len(targets))
    return targets


def combine_csv_files(input_dir, output_file):
    """Takes an input directory for files and named output file to combine the necessary .csv files"""
    csv_files = [
        f for f in listdir(input_dir)
        if f.lower().endswith('.csv')
    ]

    if not csv_files:
        logger.warning(
            "No CSV files found in '%s'; skipping combine.", input_dir)
        return

    logger.info("Combining %d CSV file(s) from '%s' into '%s'.",
                len(csv_files), input_dir, output_file)

    first_file = True

    try:
        with open(output_file, mode='w', newline='') as outfile:
            writer = csv.writer(outfile)

            for i, filename in enumerate(csv_files, start=1):
                file_path = path.join(input_dir, filename)
                logger.info("Processing CSV (%d/%d): %s",
                            i, len(csv_files), filename)

                with open(file_path, mode='r', newline='') as infile:
                    reader = csv.reader(infile)

                    if first_file:
                        for row in reader:
                            writer.writerow(row)
                        first_file = False

                    else:
                        next(reader, None)
                        for row in reader:
                            writer.writerow(row)
        logger.info("CSV combine complete: %s", output_file)

    except Exception:
        logger.exception(
            "Failed while combining CSV files in '%s'.", input_dir)
        raise


def main() -> None:
    """Main execution block"""
    configure_logging()
    logger.info("Pipeline started.")

    try:
        load_dotenv()

        output_root = "./pipeline/museum"
        if not exists("./pipeline"):
            mkdir("./pipeline")
        if not exists(output_root):
            mkdir(output_root)

        s3 = get_s3_client(ENV)
        bucket = choose_bucket(s3, ENV)

        keys = list_objects(s3, bucket)
        payload = extract_csv(keys) + extract_json(keys)

        download_objects(s3, bucket,
                         payload, output_root)

        combine_csv_files(
            input_dir=output_root,
            output_file=join(output_root, "combined.csv"),
        )
    except Exception:
        logger.exception("Pipeline failed.")
        raise


if __name__ == "__main__":
    main()
