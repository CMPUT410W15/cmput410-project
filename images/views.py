from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.http import Http404
from django.template import RequestContext
from images.models import *
from posts.models import *
from django.contrib.sites.models import Site
from django.http import HttpResponse
from PIL import Image as PIL
from api.middleware_custom import APIMiddleware

# Create your views here.
def image(request, image_id):

    if not request.user.is_authenticated():
        r = APIMiddleware().process_request(request, override=True)
        request.user = request.user.user
        if r is not None:
            return r

    try:
        obj = Image.objects.get(uid=image_id)
    except Image.DoesNotExist:
        return HttpResponseNotFound('{"message": "No such image"}')

    try:
        if not obj.visible_to(Author.objects.get(user=request.user)):
            return HttpResponse('Unauthorized', status=401)
    except Author.DoesNotExist:
            return HttpResponse('Unauthorized', status=401)

    img = PIL.open(obj.image)
    response = HttpResponse(content_type="image/png")
    img.save(response, "PNG")

    return response

def images(request):
    context = RequestContext(request)
    # Get all images
    images = [ 
        x
        for x in Image.objects.all()
        if x.visible_to(Author.objects.get(user=request.user))
    ]
    return render_to_response('all.html', {'images': images}, context)
