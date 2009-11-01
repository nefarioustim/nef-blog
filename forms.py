# -*- coding: utf-8 -*-

from django import forms
from blog.models import Comment

class ContactForm(forms.Form):
    sender = forms.EmailField(label='Your name')
    subject = forms.CharField(max_length=100)
    message = forms.CharField(widget=forms.Textarea)
    cc_myself = forms.BooleanField(label=u'I would like to receive a copy of \
    the email myself.', required=False)

class CommentForm(forms.ModelForm):
    user_name = forms.CharField(max_length=50, label='Your name')
    user_email = forms.EmailField(label='Your email')
    user_url = forms.URLField(required=False, label='Your website')
    
    class Meta:
        model = Comment
        fields = ('user_name', 'user_email', 'user_url', 'comment')