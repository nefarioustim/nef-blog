from django import template
from blog.models import Post

def do_latest_posts(parser, token):
    return LatestPostsNode()

class LatestPostsNode(template.Node):
    def render(self, context):
        context['latest_posts'] = Post.pub.all()[:3]
        return ''

register = template.Library()
register.tag('get_latest_posts', do_latest_posts)