import re
from django import forms
from django.contrib.auth.models import User
from posts.models import *
from author.models import Author
from django.utils.translation import ugettext_lazy as _
from django.db import models
from images.models import *

class PostForm(forms.Form):

    PLAINTEXT = 0
    MARKDOWN = 1
    CONTENT_TYPE = ((PLAINTEXT, 'PlainText'),
                (MARKDOWN, 'Markdown'))
    PRIVATE = 0
    FRIEND = 1
    FRIENDS = 2
    FOAF = 3
    PUBLIC = 4
    SERVERONLY = 5
    VISIBILITY = ((PUBLIC, 'Public'),
              (FRIENDS, 'Friends'),
              (FOAF, 'Friend Of A Friend'),
              (SERVERONLY, 'Server Only'),
              (PRIVATE, 'Private'),)
 
    title = forms.CharField(widget=forms.TextInput(attrs=dict(required=True, max_length=36)), label=_("Title"))
    description = forms.CharField(required=False, max_length=200)
    content = forms.CharField(widget=forms.Textarea, label=_("Content"))
    content_type = forms.ChoiceField(widget=forms.Select, choices=CONTENT_TYPE, label=_("Content Type"))
    visibility = forms.ChoiceField(widget=forms.Select, choices=VISIBILITY)
   
    #image = forms.ImageField(required=False, label=_("Attach Image:"))
    send_author = models.ForeignKey(Author)
    categories = forms.CharField(required=False, widget=forms.TextInput())

 
    def clean(self):

        return self.cleaned_data

class CommentForm(forms.Form):
    content= forms.CharField(max_length=150, label =_("Content"), required=True)

    def clean(self):
        if 'content' not in self.cleaned_data:
            raise forms.ValidationError("Can't post an empty comment!")
        else:
            return self.cleaned_data


    #  @property
    # def helper(self):
    #     helper = FormHelper()
    #     helper.form_tag = False # don't render form DOM element
    #     helper.render_unmentioned_fields = True # render all fields
    #     helper.label_class = 'col-md-2'
    #     helper.field_class = 'col-md-10'
    #     return helper

 
