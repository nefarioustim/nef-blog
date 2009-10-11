from django import template
from blog.models import Post

register = template.Library()

@register.tag(name="get_latest_posts")
def do_latest_posts(parser, token):
    return LatestPostsNode()

class LatestPostsNode(template.Node):
    def render(self, context):
        context['latest_posts'] = Post.pub.all()[:3]
        return ''