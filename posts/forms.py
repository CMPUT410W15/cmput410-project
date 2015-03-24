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
    VISIBILITY = ((PUBLIC, 'Public'),
              (FRIEND, 'Friend'),
              (FRIENDS, 'Friends'),
              (FOAF, 'Friend Of A Friend'),
              (SERVERONLY, 'Server Only'),
              (PRIVATE, 'Private'),)
 
    title = forms.CharField(widget=forms.TextInput(attrs=dict(required=True, max_length=36)), label=_("Title"))
    content = forms.CharField(widget=forms.Textarea, label=_("Content"))
    content_type = forms.ChoiceField(widget=forms.Select, choices=CONTENT_TYPE, label=_("Content Type"))
    visibility = forms.ChoiceField(widget=forms.Select, choices=VISIBILITY)
    receive_author = forms.CharField(required=False, widget=forms.TextInput(), label=_("Recipient"))
    send_author = models.ForeignKey(Author)
 
    def clean(self):

        return self.cleaned_data

    def clean_receive_author(self):
        if self.cleaned_data['receive_author'] != "":
            try:
                recipient = Author.objects.get(user=User.objects.get(username=self.cleaned_data['receive_author']))

            except User.DoesNotExist:
                raise forms.ValidationError("Recipient username is incorrect or does not exist.")


            return recipient
        else:
            return

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

 
