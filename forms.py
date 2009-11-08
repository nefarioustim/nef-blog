# -*- coding: utf-8 -*-

from django import forms
from django.conf import settings
from django.contrib.sites.models import Site
from django.utils.encoding import smart_str

from blog.models import Comment, sanitise

from akismet import Akismet

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
    
    def moderate(self, instance):
        """Comment moderation function."""
        
        akismet_api = Akismet(key=settings.AKISMET_API_KEY,
                              blog_url="http://%s/" %
                              Site.objects.get_current().domain)
        
        if akismet_api.verify_key():
            akismet_data = {
                'comment_type': 'comment',
                'referrer': '',
                'user_ip': instance.ip_address,
                'user_agent': ''
            }
            
            has_fail = akismet_api.comment_check(smart_str(instance.comment),
                                                 akismet_data,
                                                 build_data=True)
            
            if has_fail:
                instance.is_public = False
        
        instance.comment = sanitise(instance.comment)
        
        return instance