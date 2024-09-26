"""
This module contains functions for saving and loading data to and from JSON files.
"""

import json
import os


def store_to_json(data, filename: str = 'example.json') -> None:
    """
    Stores data to a JSON file.
    :param data: The data to store.
    :param filename: The name of the file to store the data in.
    """
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)


def load_from_json(filename: str = 'example.json'):
    """
    Loads data from a JSON file.
    :param filename: The name of the file to load the data from.
    :returns: The data loaded from the file.
    """
    with open(filename, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data


def list_to_json(data, filename: str = 'example.json') -> None:
    """
    Appends data to a JSON file.
    :param data: The data to append.
    :param filename: The name of the file to append the data to.
    """
    temp = load_from_json(filename) if os.path.exists(filename) else []
    temp.extend(data if isinstance(data, list) else [data])
    store_to_json(temp, filename)
