from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render_to_response
from django.contrib.auth.models import User

from author.models import Author
from posts.forms import *

@csrf_protect
def post(request):
    # Create post
    context = RequestContext(request)
    me = Author.objects.get(user=request.user)
    friends = me.get_friends()
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['receive_author']:
                post = Post.objects.create(
                    title = form.cleaned_data['title'],
                    content = form.cleaned_data['content'],
                    content_type = form.cleaned_data['content_type'],
                    visibility = form.cleaned_data['visibility'],
                    receive_author = Author(form.cleaned_data['receive_author']),
                    send_author = me,
                )
            else:
                post = Post.objects.create(
                    title = form.cleaned_data['title'],
                    content = form.cleaned_data['content'],
                    content_type = form.cleaned_data['content_type'],
                    visibility = form.cleaned_data['visibility'],
                    send_author = me,
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
