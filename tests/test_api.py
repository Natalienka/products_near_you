# -*- coding: utf-8 -*-

import pytest

@pytest.fixture(scope="module")
def request_data():
    '''Returns valid request data'''
    data = {
        'count': 3,
        'lat': 59.3325800,
        'lng': 18.0649000,
        'radius': 1000,
        'tags': ['trousers', 'shirts']
    }
    return data

def test_no_body(post):
    response = post('/search')
    assert response.status_code == 400

def test_no_tags(post, request_data):
    data = request_data.copy()
    
    data.pop('tags')
    response = post('/search', data=data)
    assert response.status_code == 200

def test_with_tags(post, request_data):
    response = post('/search', data=request_data)
    assert response.status_code == 200

def test_missing_param(post, request_data):
    data = request_data.copy()
    
    data.pop('count')
    response = post('/search', data=data)
    assert response.status_code == 400

def test_wrong_param_value(post, request_data):
    data = request_data.copy()
    
    data['count'] = -2
    response = post('/search', data=data)
    assert response.status_code == 400

    data['count'] = 'x'
    response = post('/search', data=data)
    assert response.status_code == 400