"""Generic functions shared across applications."""
import uuid


def gen_uuid():
    """Generate a hex uuid string."""
    return str(uuid.uuid1().hex)
