import json
import logging
import re
from itertools import groupby
from logging.handlers import RotatingFileHandler
from pathlib import Path

from flask import Flask
from pymemcache.client.base import Client
from pymemcache.serde import PickleSerde

IPV4_RE = re.compile(
    r"^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}"
    r"([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$"
)


def is_valid_ipv4(ip: str) -> bool:
    """
    Returns True if given IP address has IPv4 format

    Otherwise returns False
    """

    return bool(IPV4_RE.match(ip))


def convert_ipv4_to_binary(ip: str) -> str:

    """
    If given IP address has IPv4 format, converts it to 32-bit string

    Otherwise returns empty string
    """

    return (
        is_valid_ipv4(ip)
        and "".join(format(int(x), "08b") for x in ip.split("."))
        or ""
    )


def load_json_file(path: Path) -> list:
    """
    Reads json file the given `path` and returns list of python dictionariers
    """

    file_path = Path(path).resolve()
    with open(file_path, "r") as file:
        data = json.load(file)

    return data


def prepare_data_to_db(path: Path) -> list:
    """
    Prepares data for loading to database. Returns a list of dicts with keys:
    - `binary_network_part`: an unique identifier of an ip network address
                             (a binary representation of a network part of an
                             IP network address, like `00001010` for `10.0.0.0/8`)
    - `tags`: json serialized sorted list of unique tags connected
              with IP network address (`binary_network_part`)
    """

    prepared_data = []

    # loading raw data from json file
    data = load_json_file(path)

    # adding new attribute `binary_network_part`
    for el in data:
        net_address, net_digits = el["ip_network"].split("/")
        net_digits = int(net_digits)
        net_address_binary = convert_ipv4_to_binary(net_address)
        el["binary_network_part"] = net_address_binary[:net_digits]

    # grouping `tags` in data by `binary_network_part` attribute
    # tags in lists are unique, sorted and serialized
    data.sort(key=lambda x: x["binary_network_part"])
    for key, group in groupby(data, key=lambda x: x["binary_network_part"]):
        sorted_unique_tags_list = sorted(list(set([el["tag"] for el in group])))

        prepared_data.append(
            {"binary_network_part": key, "tags": json.dumps(sorted_unique_tags_list)}
        )

    return prepared_data


def setup_logging(app: Flask) -> None:
    """
    Initiates logging for given Flask app
    """

    logging.basicConfig(
        handlers=[
            logging.StreamHandler(),
            RotatingFileHandler(
                filename=app.config["LOG_FILE_PATH"],
                maxBytes=app.config["LOG_MAX_BYTES"],
                backupCount=app.config["LOG_BACKUP_COUNT"],
            ),
        ],
        format="[%(asctime)s] %(levelname)s "
        "[%(name)s.%(funcName)s:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

    app.logger.setLevel(app.config["LOG_LEVEL"])


def setup_cache(app: Flask) -> None:
    """
    Initiates memcached caching
    """
    try:

        app.cache = Client(
            app.config["MEMCACHED_SERVER"] + "1",
            serde=PickleSerde(pickle_version=2),
            connect_timeout=5,
            timeout=1,
            ignore_exc=True,
        )

    except Exception:
        app.logger.error("Error in setup cache", exc_info=True)
