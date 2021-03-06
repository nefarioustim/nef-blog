import logging
from datetime import date

from django.forms.widgets import CheckboxInput
from django.core.mail import send_mail, mail_managers
from django.shortcuts import render_to_response, get_object_or_404, redirect
from blog.models import Category, Post
from blog.forms import ContactForm, CommentForm

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    return render_to_response('blog/category_detail.html', {
        'object_list': category.pub_post_set(),
        'cat': category
    })

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        
        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            sender = form.cleaned_data['sender']
            cc_myself = form.cleaned_data['cc_myself']
            
            if cc_myself:
                recipients = [sender]
                send_mail(subject, message, sender, recipients)
            
            message = "From: %s\n\n%s" % (sender, message)
            
            mail_managers(subject, message)
            
            return redirect('blog.views.contact_thanks')
    else:
        form = ContactForm()
    
    return render_to_response('blog/contact.html', {
        'form': form,
    })

def contact_thanks(request):
    return render_to_response('blog/contact_thanks.html', {})

def post_index(request):
    return render_to_response('blog/post_index.html', {
        'post_list': Post.pub.all()[:3],
        'started_webdev': date(2000, 8, 29),
    })

def post_detail(request, slug):
    post = get_object_or_404(Post.pub, slug=slug)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.ip_address = request.META.get("REMOTE_ADDR", None)
            comment = form.moderate(comment)
            comment.save()
            
            email_body = "%s posted a new comment on the post '%s'."
            mail_managers("New comment posted", email_body %
                          (comment.user_name, post))
            
            return redirect('blog.views.post_detail', slug=post.slug)
    else:
        form = CommentForm()
    
    return render_to_response('blog/post_detail.html', {
        'post': post,
        'form': form,
    })