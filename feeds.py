from django.contrib.syndication.feeds import Feed
from django.utils.feedgenerator import Atom1Feed

from blog.models import Category, Post

class RssFeed(Feed):
    title = "Vidjagam.es"
    link = "/sitenews/"
    description = "The latest European news and views on computer and video \
    gaming."

    def items(self):
        return Post.pub.order_by('-pub_date')[:5]

class AtomFeed(RssFeed):
    feed_type = Atom1Feed
    subtitle = RssFeed.description