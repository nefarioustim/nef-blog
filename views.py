from datetime import date

from django.shortcuts import render_to_response, get_object_or_404
from blog.models import Category, Post

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    return render_to_response('blog/category_detail.html', {
        'object_list': category.pub_post_set(),
        'cat': category
    })

def post_index(request):
    return render_to_response('blog/post_index.html', {
        'post_list': Post.pub.all()[:3],
        'started_webdev': date(2000, 8, 29),
    })

def post_detail(request, slug):
    post = get_object_or_404(Post.pub, slug=slug)
    return render_to_response('blog/post_detail.html', {
        'post': post
    })