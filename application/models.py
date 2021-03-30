import json
from itertools import chain

from flask import current_app
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text

from application.utils import convert_ipv4_to_binary

db = SQLAlchemy()
migrate = Migrate()


class NetworkTag(db.Model):
    """
    NetworkTag model with two fields:
    binary_network_part - binary representation of network
                          part of IP network address
    tags - unique list of tags linked to IP network address
    """

    __tablename__ = "network_tags"

    binary_network_part = db.Column(db.String(32), primary_key=True)
    tags = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.binary_network_part}>"

    @staticmethod
    def _get_many_objects(binary_parts_list: list) -> list:
        """ Helper function for obtaining several binary ip networks """

        filter_expression = text(
            " or ".join(
                [
                    f"binary_network_part = '{binary_part}'"
                    for binary_part in binary_parts_list
                ]
            )
        )

        return NetworkTag.query.filter(filter_expression).all()

    @staticmethod
    def get_tags_for_ip(ip: str) -> str:
        """
        Function checks an ip addres in cache and returning it if exists
        Otherwise returns data from database and set the result in cache
        Returning data are deserialized
        """

        ip_binary = convert_ipv4_to_binary(ip)
        ip_binary_parts = [ip_binary[: index + 1] for index in range(32)]

        tags_dict = current_app.cache.get_many(ip_binary_parts)

        if not tags_dict:
            raw_objects = NetworkTag._get_many_objects(ip_binary_parts)
            tags_dict = dict(
                map(lambda x: (x.binary_network_part, x.tags), raw_objects)
            )

            current_app.cache.set_many(
                tags_dict, expire=current_app.config["CACHE_DEFAULT_TIMEOUT"]
            )

        list_of_tags_list = [json.loads(el) for el in tags_dict.values()]

        sorted_unique_tags_list = json.dumps(
            sorted(set(chain.from_iterable(list_of_tags_list)))
        )

        return json.loads(sorted_unique_tags_list)

    @staticmethod
    def fill_in_cache(records_limit: int) -> None:
        """
        Filling in the cache memory with the data from the `network_tags` table
        """

        all_network_tag_objects = NetworkTag.query.limit(records_limit).all()

        if all_network_tag_objects:
            data = dict(
                map(lambda x: (x.binary_network_part, x.tags), all_network_tag_objects)
            )

            current_app.cache.set_many(data)
