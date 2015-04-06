'''
Middleware to wrap API calls with appropriate headers and check for
authentication
'''

from django.http import HttpResponse
from django.conf import settings
from re import compile

from management.models import *
from author.models import *

import base64

class APIMiddleware:

    def process_request(self, request, override=False):

        # only process API endpoints
        if not override and not request.path.startswith('/api'):
            return

        # Check auth header existence
        if 'HTTP_AUTHORIZATION' not in request.META:
             return HttpResponse('{"message": "Must authenticate"}', status=401)

        # Check auth header validity
        http_auth = request.META['HTTP_AUTHORIZATION']
        if not http_auth.startswith("Basic ") or http_auth.count(' ') != 1:
            return HttpResponse('{"message": "Authentication Rejected"}', status=401)

        decoded = base64.b64decode(http_auth.split()[1])

        # Check for presence of user host and password
        try:
            uid, host, password = decoded.split(':')
        except:
            return HttpResponse('{"message": "Authentication Rejected"}', status=401)

        node = Node.objects.filter(url=host)
        # Check if node exists
        if not node.exists():
            return HttpResponse('{"message": "Authentication Rejected"}', status=401)

        # Check for correct password
        if password != node.password:
            return HttpResponse('{"message": "Authentication Rejected"}', status=401)

        # Monkey-patch in user to request object
        try:
            # For a known user, grab their Author object
            request.user = Author.objects.get(uid=uid)
        except:
            # For unknown user, mock-up a new Author object
            request.user = Author()
            request.user.uid = uid
            request.user.host = host

    '''
    Wrap API responses with appropriate headers
    '''
    def process_response(self, request, response):
        # only process API endpoints
        if not request.path.startswith('/api'):
            return response

        response['Content-Type'] = 'application/json'
        return response
