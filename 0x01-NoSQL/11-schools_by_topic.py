#!/usr/bin/env python3
""" Module for using PyMongo """


def schools_by_topic(mongo_collection, topic):
    """ Inserts new document in collection based on kwargs """
    schools = mongo_collection.find({"topics": topic})
    return list(schools)
