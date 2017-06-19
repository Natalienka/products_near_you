# -*- coding: utf-8 -*-

import os
import csv
import bisect
from haversine import haversine

class Database:

    def __init__(self):
        self.shops = []

    def get_most_popular_products(self, num_products, lat, lng, radius, tags=None):
        """Return the most popular products from shops from given area with given tags."""
        if tags is None:
            tags = []

        # [(shop, distance)]
        relevant_shops = []
        for shop in self.shops.values():
            distance = shop.distance(lat, lng)
            if distance < radius and shop.has_tags(tags):
                relevant_shops.append((shop, distance))

        # select (at most) num_products products from each relevant shop
        # and sort them by popularity and distance
        # [(product, shop, distance)]
        products = []
        for shop, distance in relevant_shops:
            products += [(product, shop, distance) for product in shop.products[:num_products]]
        products.sort(key=lambda x: (x[0], x[2]))

        return [{
            'product_id': product.product_id,
            'product_title': product.title,
            'product_popularity': product.popularity,
            'product_quantity': product.quantity,
            'shop_id': shop.shop_id,
            'shop_name': shop.name,
            'shop_tags': tags,
            'lat': shop.lat,
            'lng': shop.lng,
            'distance': distance
        } for product, shop, distance in products[:num_products]]

    def load(self, path):
        """Load the database."""
        shops = self._load_shops(path)
        self._load_tags(path, shops)
        self._load_products(path, shops)
        self.shops = shops

    def _load_shops(self, path):
        with open(os.path.join(path, 'shops.csv'), 'rb') as csvfile:
            reader = csv.reader(csvfile)
            next(reader) # skip header
            shops = dict(
                (row[0], Shop(id=row[0], name=row[1], lat=float(row[2]), lng=float(row[3])))
                for row in reader
            )
            return shops

    def _load_tags(self, path, shops):
        with open(os.path.join(path, 'tags.csv'), 'rb') as csvfile:
            reader = csv.reader(csvfile)
            next(reader) # skip header
            tags = dict((row[0], row[1]) for row in reader)

        with open(os.path.join(path, 'taggings.csv'), 'rb') as csvfile:
            reader = csv.reader(csvfile)
            next(reader) # skip header
            for row in reader:
                shop_id = row[1]
                tag_id = row[2]
                if (shop_id in shops) and (tag_id in tags):
                    shop = shops[shop_id]
                    shop.add_tag(tags[tag_id])

    def _load_products(self, path, shops):
        with open(os.path.join(path, 'products.csv'), 'rb') as csvfile:
            reader = csv.reader(csvfile)
            next(reader) # skip header
            for row in reader:
                shop_id = row[1]
                if shop_id in shops:
                    shop = shops[shop_id]
                    shop.add_product(Product(id=row[0], title=row[2], popularity=row[3], quantity=row[4]))


class Product:

    def __init__(self, id, title, popularity, quantity):
        self.product_id = id
        self.title = title
        self.popularity = popularity
        self.quantity = quantity

    def __cmp__(self, other):
        if self.popularity < other.popularity:
            return 1
        elif self.popularity > other.popularity:
            return -1
        else:
            return 0

class Shop:

    def __init__(self, id, name, lat, lng, tags=None, products=None):
        self.shop_id = id
        self.name = name
        self.lat = lat
        self.lng = lng
        self.tags = [] if tags is None else tags
        self.products = [] if products is None else products

    def add_tag(self, tag):
        """Add a tag to this shop"""
        bisect.insort(self.tags, tag)

    def add_product(self, product):
        """Add a product to this shop."""
        bisect.insort(self.products, product)

    def distance(self, lat, lng):
        """Return distance from given location."""
        return haversine((lat, lng), (self.lat, self.lng)) * 1000

    def has_tags(self, tags):
        """Check whether this shop has at least one tag from given list of tags.
        If empty list is given as a parameter, method always returns True.
        """
        if len(tags) == 0:
            return True

        for tag in tags:
            if self.hasTag(tag):
                return True
        return False

    def hasTag(self, tag):
        """Check whether this shop has a tag."""
        i = bisect.bisect(self.tags, tag)
        if i == 0:
            return 0
        elif self.tags[i-1] == tag:
            return 1
        else:
            return 0
