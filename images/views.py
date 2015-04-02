from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from images.models import *
from django.contrib.sites.models import Site
from django.http import HttpResponse

# Create your views here.
def get_image(request, uid):
    image = Image.objects.get(uid=uid)

    return HttpResponse(image.read())

def images(request):
    context = RequestContext(request)
    # Get all images
    images = Image.objects.all()
    return render_to_response('all.html', {'images': images}, context)
