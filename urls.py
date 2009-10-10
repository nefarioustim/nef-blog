from django.conf.urls.defaults import *

from blog.models import Category, Post
from blog.feeds import RssFeed, AtomFeed

urlpatterns = patterns('blog.views',
    (r'^$', 'post_index'),
    (r'^contact/$', 'contact'),
    (r'^contact/thanks.html$', 'contact_thanks'),
    (r'^(?P<slug>[-\w]+)\.html$', 'post_detail'),
    (r'^categories/(?P<slug>[-\w]+)/$', 'category_detail'),
)

feeds_dict = {
    'rss': RssFeed,
    'atom': AtomFeed,
}

urlpatterns += patterns('',
    (r'^comments/', include('django.contrib.comments.urls')),
    (r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed', {'feed_dict': feeds_dict}),
)

urlpatterns += patterns('',
    (r'^categories/$', 'django.views.generic.list_detail.object_list', {
        'queryset': Category.objects.all()
    }),
)

post_info_dict = {
    'queryset': Post.pub.all(),
    'date_field': 'pub_date',
}

urlpatterns += patterns('django.views.generic.date_based',
    (r'^archive/$', 'archive_index', post_info_dict),
    (r'^archive/(?P<year>\d{4})/$', 'archive_year', post_info_dict),
    (r'^archive/(?P<year>\d{4})/(?P<month>\w+?)/$', 'archive_month', dict(
        post_info_dict.items() + [('month_format', '%B')]
    )),
)