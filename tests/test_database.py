# -*- coding: utf-8 -*-

import os
import shutil
import csv
import pytest

from server.database import Database

@pytest.fixture(scope="module")
def database():
    '''Returns a pre-loaded Database instance'''
    parent = os.path.dirname(__file__)
    path = os.path.join(parent, '..', 'test_data')
    prepare_csv_files(path)
    db = Database()
    db.load(path)
    shutil.rmtree(path)
    return db

def prepare_csv_files(path):
    if not os.path.exists(path):
        os.makedirs(path)
    with open(os.path.join(path, 'shops.csv'), 'wb') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['id', 'name', 'lat', 'lng'])
        writer.writerow(['shop1', 'Shop 1', '59.3326', '18.0606'])
        writer.writerow(['shop2', 'Shop 2', '59.3332', '18.0997'])
        writer.writerow(['shop3', 'Shop 3', '59.3456', '18.1234'])

    with open(os.path.join(path, 'tags.csv'), 'wb') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['id', 'tag'])
        writer.writerow(['tag1', 'Tag 1'])
        writer.writerow(['tag2', 'Tag 2'])

    with open(os.path.join(path, 'taggings.csv'), 'wb') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['id', 'shop_id', 'tag_id'])
        writer.writerow(['tagging1', 'shop3', 'tag1'])
        writer.writerow(['tagging2', 'shop2', 'tag2'])

    with open(os.path.join(path, 'products.csv'), 'wb') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['id', 'shop_id', 'title', 'popularity', 'quantity'])
        writer.writerow(['product1', 'shop1', 'Product 1', '0.5', '5'])
        writer.writerow(['product2', 'shop1', 'Product 2', '0.7', '1'])
        writer.writerow(['product3', 'shop2', 'Product 3', '0.1', '2'])
        writer.writerow(['product4', 'shop2', 'Product 4', '0.6', '3'])
        writer.writerow(['product5', 'shop3', 'Product 5', '0.9', '1'])
        writer.writerow(['product6', 'shop3', 'Product 6', '0.1', '10'])

def test_small_radius(database):
    # no shops
    products = database.get_most_popular_products(3, 59.3329, 18.0805, 1000)
    assert len(products) == 0

def test_medium_radius_no_tags(database):
    # only shops 1 and 2
    products = database.get_most_popular_products(2, 59.3329, 18.0805, 2000)
    assert len(products) == 2
    assert products[0]['product_id'] == 'product2'
    assert products[1]['product_id'] == 'product4'

def test_medium_radius_tags(database):
    # no shops
    products = database.get_most_popular_products(2, 59.3329, 18.0805, 2000, ['Tag 1'])
    assert len(products) == 0

def test_large_radius_no_tags(database):
    # all shops
    products = database.get_most_popular_products(2, 59.3329, 18.0805, 3000)
    assert len(products) == 2
    assert products[0]['product_id'] == 'product5'
    assert products[1]['product_id'] == 'product2'

def test_large_radius_tags(database):
    # only shop 3
    products = database.get_most_popular_products(2, 59.3329, 18.0805, 3000, ['Tag 1'])
    assert len(products) == 2
    assert products[0]['product_id'] == 'product5'
    assert products[1]['product_id'] == 'product6'

def test_large_radius_multiple_tags(database):
    # only shops 2 and 3
    products = database.get_most_popular_products(2, 59.3329, 18.0805, 3000, ['Tag 1', 'Tag 2'])
    assert len(products) == 2
    assert products[0]['product_id'] == 'product5'
    assert products[1]['product_id'] == 'product4'

def test_large_radius_too_many_products(database):
    # all shops
    products = database.get_most_popular_products(10, 59.3329, 18.0805, 3000)
    assert len(products) == 6
    assert products[0]['product_id'] == 'product5'
    assert products[1]['product_id'] == 'product2'
    assert products[2]['product_id'] == 'product4'
    assert products[3]['product_id'] == 'product1'
    assert products[4]['product_id'] == 'product3'
    assert products[5]['product_id'] == 'product6'
