import os
import csv
import pytest
from unittest.mock import MagicMock, patch, mock_open

import extract


@patch("extract.client")
def test_get_s3_client(mock_boto_client):
    # Arrange
    config = {
        "AWS_ACCESS_KEY": "key",
        "AWS_SECRET_KEY": "secret"
    }

    # Act
    extract.get_s3_client(config)

    # Assert
    mock_boto_client.assert_called_once_with(
        service_name="s3",
        aws_access_key_id="key",
        aws_secret_access_key="secret"
    )


def test_list_buckets():
    mock_s3 = MagicMock()
    mock_s3.list_buckets.return_value = {
        "Buckets": [
            {"Name": "bucket-a"},
            {"Name": "bucket-b"}
        ]
    }

    buckets = extract.list_buckets(mock_s3)

    assert buckets == ["bucket-a", "bucket-b"]


def test_extract_csv():
    objects = [
        "lmnh_hist_data_2020.csv",
        "lmnh_hist_data_2021.csv",
        "lmnh_exhibition_a.json",
        "random.txt"
    ]

    result = extract.extract_csv(objects)

    assert result == [
        "lmnh_hist_data_2020.csv",
        "lmnh_hist_data_2021.csv"
    ]


def test_extract_json():
    objects = [
        "lmnh_exhibition_a.json",
        "lmnh_exhibition_b.json",
        "lmnh_hist_data_2021.csv",
        "random.txt"
    ]

    result = extract.extract_json(objects)

    assert result == [
        "lmnh_exhibition_a.json",
        "lmnh_exhibition_b.json"
    ]


@patch("extract.validate_parent_dir")
def test_download_objects(mock_validate_dir):
    mock_s3 = MagicMock()
    keys = ["a.csv", "b/c.csv"]

    extract.download_objects(
        s3_client=mock_s3,
        bucket_name="bucket",
        keys=keys,
        output_dir="out"
    )

    assert mock_s3.download_file.call_count == 2
    mock_s3.download_file.assert_any_call(
        Bucket="bucket",
        Key="a.csv",
        Filename="out/a.csv"
    )

    mock_s3.download_file.assert_any_call(
        Bucket="bucket",
        Key="b/c.csv",
        Filename="out/b/c.csv"
    )


@patch("extract.listdir")
def test_combine_no_csv(mock_listdir):
    mock_listdir.return_value = []

    extract.combine_csv_files("input", "output.csv")
