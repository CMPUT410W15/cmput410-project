"""Generic functions shared across applications."""
import uuid

import requests
from management.models import Node


def gen_uuid():
    """Generate a hex uuid string."""
    return str(uuid.uuid1().hex)

def get_request_to_json(url):
    req = requests.get(url)
    return req.json()

def get_nodes():
    ignore = ['host', '127.0.0.1:8000', '127.0.0.1', 'localhost']
    all_nodes = Node.objects.all()
    return [n for n in all_nodes if n.url not in ignore]
