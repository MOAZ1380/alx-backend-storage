#!/usr/bin/env python3
""" Module for using PyMongo """


def update_topics(mongo_collection, name, topics):
    """ Inserts new document in collection based on kwargs """
    mongo_collection.update_many(
        {"name": name},
        {"$set": {"topics": topics}}
    )
