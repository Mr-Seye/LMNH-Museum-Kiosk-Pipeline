from extract import get_s3_client, list_objects, download_objects, extract_csv, choose_bucket, combine_csv_files
from psycopg2 import Error, connect
from os import environ as ENV, _Environ, mkdir, listdir, path
from os.path import exists, join, dirname

import pandas as pd

from dotenv import load_dotenv


def get_db_connection():
    """Returns database connection"""
    try:
        connection = connect(
            dbname=ENV["DB_NAME"],
            user=ENV["DB_USERNAME"],
            password=ENV['DB_PASSWORD'],
            host=ENV['DB_HOST'],
            port=ENV["DB_PORT"]
        )
        return connection
    except Error as e:
        print(f"Error connecting to database: {e}")
        return None


if __name__ == "__main__":

    load_dotenv()

    output_root = "./pipeline/museum"
    if not exists("./pipeline"):
        mkdir("./pipeline")
    if not exists(output_root):
        mkdir(output_root)

    s3 = get_s3_client(ENV)
    bucket = choose_bucket(s3, ENV)

    keys = list_objects(s3, bucket)
    payload = extract_csv(keys)

    download_objects(s3, bucket,
                     payload, output_root)

    combine_csv_files(
        input_dir=output_root,
        output_file=join(output_root, "combined.csv")
    )
    conn = get_db_connection()

    dataframe = pd.read_csv("./pipeline/museum/combined.csv")

    df_request = dataframe
    ratings = dataframe[dataframe["type"].isna()]
    request = dataframe[dataframe["type"].notna()]
    ratings.drop(columns="type", inplace=True)

    request = request.rename(columns={
        "site": "exhibition_id",
        "type": "request_id",
        "at": "event_at"
    })

    ratings = ratings.rename(columns={
        "site": "exhibition_id",
        "val": "rating_id",
        "at": "event_at"
    })

    ratings['event_at'] = pd.to_datetime(ratings['event_at'])
    request['event_at'] = pd.to_datetime(request['event_at'])

    print(request.head())

    with conn.cursor() as cur:
        rows = [(int(r.exhibition_id), int(r.request_id), r.event_at)
                for r in request.itertuples(index=False)]

        query = """
            INSERT INTO
                request_interaction(exhibition_id, request_id, event_at)
            VALUES
                (%s, %s, %s)
            ;
"""

        cur.executemany(query, rows)
        conn.commit()

        rows = [(int(r.exhibition_id), int(r.rating_id), r.event_at)
                for r in ratings.itertuples(index=False)]

        query = """
            INSERT INTO
                rating_interaction(exhibition_id, rating_id, event_at)
            VALUES
                (%s, %s, %s)
            ;
"""
        cur.executemany(query, rows)
        conn.commit()
    conn.close()
