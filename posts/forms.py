import re
from django import forms
from django.contrib.auth.models import User
from posts.models import Post
from author.models import Author
from django.utils.translation import ugettext_lazy as _
from django.db import models
 
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
    VISIBILITY = ((PRIVATE, 'Private'),
              (FRIEND, 'Friend'),
              (FRIENDS, 'Friends'),
              (FOAF, 'Friend Of A Friend'),
              (PUBLIC, 'Public'),
              (SERVERONLY, 'Server Only'))
 
    title = forms.CharField(widget=forms.TextInput(attrs=dict(required=True, max_length=36)), label=_("Title"))
    content = forms.CharField(widget=forms.Textarea, label=_("Content"))
    content_type = forms.ChoiceField(widget=forms.Select, choices=CONTENT_TYPE, label=_("Content Type"))
    visibility = forms.ChoiceField(widget=forms.Select, choices=VISIBILITY)
    receive_author = forms.CharField(required=False, widget=forms.TextInput(), label=_("Recipient"))
    send_author = models.ForeignKey(Author)
 
    def clean(self):
       
        return self.cleaned_data

    def clean_recipient(self):
        try:
            recipient = User.objects.get(username__iexact=self.cleaned_data['username'])
        except:
        	pass

        return recipient

 
