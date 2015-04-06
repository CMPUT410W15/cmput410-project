import re
from django import forms
from django.contrib.auth.models import User
from posts.models import *
from author.models import Author
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.forms import ImageField

#Used to update the github, picture and email of a user.
class UserUpdateForm(forms.Form):
    email = forms.CharField(required=False,max_length=30, label=_("Email address"))
    github = forms.CharField(max_length=100,required=False, label=_('Github account'))
    picture = forms.ImageField(required=False, label=_("Attach Profile Image"))

 
