from django.conf.urls.defaults import *

from blog.models import Category, Post

post_info_dict = {
    'queryset': Post.pub.all(),
    'date_field': 'pub_date',
}

urlpatterns = patterns('blog.views',
    (r'^$', 'post_index'),
    (r'^(?P<slug>[-\w]+)\.html$', 'post_detail'),
    (r'^categories/(?P<slug>[-\w]+)/$', 'category_detail'),
)

urlpatterns += patterns('',
    (r'^comments/', include('django.contrib.comments.urls'))
)

urlpatterns += patterns('',
    (r'^categories/$', 'django.views.generic.list_detail.object_list', {
        'queryset': Category.objects.all()
    }),
)

urlpatterns += patterns('django.views.generic.date_based',
    (r'^archive/$', 'archive_index', post_info_dict),
    (r'^archive/(?P<year>\d{4})/$', 'archive_year', post_info_dict),
    (r'^archive/(?P<year>\d{4})/(?P<month>\w+?)/$', 'archive_month', dict(
        post_info_dict.items() + [('month_format', '%B')]
    )),
)