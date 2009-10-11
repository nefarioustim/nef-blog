# -*- coding: utf-8 -*-

from django import forms

class ContactForm(forms.Form):
    sender = forms.EmailField(label='Your name')
    subject = forms.CharField(max_length=100)
    message = forms.CharField(widget=forms.Textarea)
    cc_myself = forms.BooleanField(label=u'“I would like to receive a copy of \
    the email myself.”', required=False)