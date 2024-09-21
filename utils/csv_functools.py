"""
This module contains functions to store, load and append data to a CSV file.
"""

import csv
import os
from typing import Dict, List


def store_to_csv(data, filename: str = 'example.csv') -> None:
    """
    Store data to a CSV file
    :param data: The data to store
    :param filename: The name of the file
    """
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=data.keys())
        writer.writeheader()
        writer.writerow(data)


def load_from_csv(filename: str = 'example.csv') -> List[Dict]:
    """
    Load data from a CSV file
    :param filename: The name of the file
    :return: A list of dictionaries
    """
    with open(filename, 'r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        return list(reader)


def append_to_csv(data, filename: str = 'example.csv') -> None:
    """
    Append data to a CSV file
    :param data: The data to append
    :param filename: The name of the file
    """
    file_exists = os.path.exists(filename)

    with open(filename, 'a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=data.keys())

        if not file_exists:
            writer.writeheader()

        writer.writerow(data)
