# -*- coding: utf-8 -*-

from flask import Blueprint, current_app, jsonify, request, abort

api = Blueprint('api', __name__)

'''
def data_path(filename):
    data_path = current_app.config['DATA_PATH']
    return u"%s/%s" % (data_path, filename)
'''

def get_database():
    return current_app.config['DATABASE']

@api.route('/search', methods=['POST'])
def search():
    content = request.json
    count, lat, lng, radius, tags = get_validated_search_parameters(content)
    database = get_database()
    products = database.get_most_popular_products(count, lat, lng, radius, tags)
    grouped_products = group_products_by_shop(products)

    return jsonify({'shops': [shop for shop in grouped_products.values()]})

def get_validated_search_parameters(content):
    """Validate and return search parameters"""
    if content is None:
        abort(400, 'Invalid input: missing request body.')
    try:
        count = int(content['count'])
        lat = float(content['lat'])
        lng = float(content['lng'])
        radius = float(content['radius'])
        tags = content.get('tags')
        if tags is not None and not isinstance(tags, list):
            raise ValueError
        if count < 0:
            raise ValueError
    except KeyError as error:
        abort(400, 'Invalid input: missing search parameter "{}".'.format(error.args[0]))
    except ValueError:
        abort(400, 'Invalid input: invalid search parameter value.')
 
    max_radius = 5000
    if radius > max_radius:
        abort(400, 'Invalid input: search radius cannot be larger than {}m.'.format(max_radius))

    return count, lat, lng, radius, tags


def group_products_by_shop(products):
    """Group given list of products by the same shop."""
    grouped_products = {}
    for product in products:
        shop_id = product['shop_id']
        if shop_id not in grouped_products:
            grouped_products[shop_id] = {
                'name': product['shop_name'],
                'lat': product['lat'],
                'lng': product['lng'],
                'distance': product['distance'],
                'tags': product['shop_tags'],
                'products': []
            }
        grouped_products[shop_id]['products'].append({
            'title': product['product_title'],
            'popularity': product['product_popularity'],
            'quantity': product['product_quantity']
        })
    return grouped_products
