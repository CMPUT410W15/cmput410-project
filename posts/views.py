from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render_to_response
from django.contrib.auth.models import User

from author.models import Author
from posts.models import Post
from posts.forms import *
from login.views import *

@csrf_protect
def post(request):
    # Create post
    context = RequestContext(request)
    me = Author.objects.get(user=request.user)
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            visibility = form.cleaned_data['visibility']
            receive_author = form.cleaned_data['receive_author']
            if receive_author:
                post = Post.objects.create(
                    title=form.cleaned_data['title'],
                    content=form.cleaned_data['content'],
                    content_type=form.cleaned_data['content_type'],
                    visibility=form.cleaned_data['visibility'],
                    receive_author=Author.objects.get(user=User.objects.get(username=receive_author)),
                    send_author=me,
                )
                post.save()
            else:
                post = Post.objects.create(
                    title=form.cleaned_data['title'],
                    content=form.cleaned_data['content'],
                    content_type=form.cleaned_data['content_type'],
                    visibility=form.cleaned_data['visibility'],
                    send_author=me,
                )
                post.save()
            return HttpResponseRedirect('/home')
    else:
        form = PostForm()
    variables = RequestContext(request, {'form': form})

    return render_to_response(
        'posting.html',
        variables,
    )

def delete_post(request, uid):
    context = RequestContext(request)
    Post.objects.filter(uid=uid).delete()
    return HttpResponseRedirect('/home')

def comment(request,post_id):
    #Create a comment on a post
    context= RequestContext(request)
    me = Author.objects.get(user=request.user)

    args={}
    #Get the post to comment on
    post= Post.objects.get(uid=post_id)
    # content= request.POST.get('content')
    # post.add_comment(me,content)
    # post.save()

    # return HttpResponseRedirect('/home')
#http://stackoverflow.com/questions/22470637/django-show-validationerror-in-template
    if request.method == "POST":
        form= CommentForm(request.POST)
        if form.is_valid():
            content= form.cleaned_data["content"]
            post.add_comment(me,content)
            post.save()
            return HttpResponseRedirect('/home')
    else:
        form= CommentForm()
    args['form']=form

    #Return to home page with the args dict to render errors.
    return home(request,args)
    #return HttpResponseRedirect('/home')
    # return render(request, 'commenting.html', {'form':form})
