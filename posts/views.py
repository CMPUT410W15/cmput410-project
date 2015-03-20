from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render_to_response
from django.contrib.auth.models import User
from django.http import HttpResponse
from author.models import Author
from posts.models import Post
from posts.forms import *
from login.views import *
import json
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

@csrf_protect
def comment(request,post_id):

    #Create a comment on a post
    context= RequestContext(request)
    me = Author.objects.get(user=request.user)
    args={}
    #Get the post to comment on
    post= Post.objects.get(uid=post_id)

    if request.method == "POST":
        comment_text= request.POST.get('the_comment')
        response_data={}

        #If the comment is blank, return an error
        if comment_text== "":
            #Return status code 404 to indicate error
            return HttpResponse(status=404)
        else:
            post.add_comment(me,comment_text)
            post.save()
            response_data['content']= comment_text
            return HttpResponse(json.dumps(response_data), content_type="application/json")
    else:
        return HttpResponse(json.dumps({"nothing here": "this won't happen"}), content_type="application/json")

