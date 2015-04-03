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
from images.models import *
import json
from django.http import QueryDict

@csrf_protect
def post(request):
    # Create post
    context = RequestContext(request)
    me = Author.objects.get(user=request.user)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            #Check if an image was uploaded before attempting to save an image or a post
            # with a image 
            if 'image' in request.FILES:
                image = Image.objects.create(
                    image = request.FILES['image'],
                    visibility=form.cleaned_data['visibility'], 
                    )
                image.save()
                
            else:

                image = None

            post = Post.objects.create(
                title=form.cleaned_data['title'],
                description =form.cleaned_data['description'],
                content=form.cleaned_data['content'],
                content_type=form.cleaned_data['content_type'],
                visibility=form.cleaned_data['visibility'],
                send_author=me,
                image = image,
            )
            post.save()

            categories = form.cleaned_data['categories']
            category = categories.split(',')
            for c in category:
                c = c.strip()
                
                try:
                    post.categories.add(Category.objects.create(category = c))
                except:
                    # Category already exists does not need to  be added.
                    print "Category " + c + " already exists and was not added."
                    
                post.save()

            return HttpResponseRedirect('/home')
    else:
        form = PostForm()
    variables = RequestContext(request, {'form': form})

    return render_to_response(
        'posting.html',
        variables,
    )

# def delete_post(request, uid):
#     context = RequestContext(request)
#     Post.objects.filter(uid=uid).delete()
#     return HttpResponseRedirect('/home')

def handle_uploaded_file(f):
    destination = open(settings.MEDIA_ROOT, 'wb+')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()


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
            #Display username with the comment
            username=request.user.username
            response_data['content']= username+": "+comment_text
            return HttpResponse(json.dumps(response_data), content_type="application/json")
    else:
        return HttpResponse(json.dumps({"nothing here": "this won't happen"}), content_type="application/json")

def delete_post(request):

    if request.method == 'DELETE':
        post = Post.objects.get(uid=QueryDict(request.body).get('post_id'))
        post.delete()
        response_data = {}
        response_data['msg'] = 'Post was deleted.'

        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )
    else:
        return HttpResponse(
            json.dumps({"nothing to see": "this isn't happening"}),
            content_type="application/json"
        )