from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render_to_response

from author.models import Author
from posts.forms import *
from django.contrib.auth.decorators import login_required

@csrf_protect
def post(request):
    # Create post
    context = RequestContext(request)
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = Post.objects.create(
                title = form.cleaned_data['title'],
                content = form.cleaned_data['content'],
                content_type = form.cleaned_data['content_type'],
                visibility = form.cleaned_data['visibility'],
                receive_author = form.cleaned_data['receive_author'],
                send_author= Author(user=user)
            )
            post.save()
            return HttpResponseRedirect('/home')
    else:
        form = PostForm()
    variables = RequestContext(request, {
    'form': form
    })
 
    return render_to_response(
    'posting.html',
    variables,
    )
