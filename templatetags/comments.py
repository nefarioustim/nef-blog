from django import template
from django.conf import settings
from blog.models import Post, Comment

register = template.Library()

class BaseCommentNode(template.Node):
    """
    Base helper class (abstract) for handling the get_comment_* template tags.
    Looks a bit strange, but the subclasses below should make this a bit more
    obvious.
    """
    
    @classmethod
    def handle_token(cls, parser, token):
        """Class method to parse get_comment_list/count and return a Node."""
        tokens = token.contents.split()
        if tokens[1] != 'for':
            raise template.TemplateSyntaxError("Second argument in %r tag must be 'for'" % tokens[0])
        
        # {% get_whatever for obj as varname %}
        if len(tokens) == 5:
            if tokens[3] != 'as':
                raise template.TemplateSyntaxError("Third argument in %r must be 'as'" % tokens[0])
            return cls(
                object_expr = parser.compile_filter(tokens[2]),
                as_varname = tokens[4],
            )
        
        else:
            raise template.TemplateSyntaxError("%r tag requires 4 arguments" % tokens[0])
    
    def __init__(self, object_expr=None, as_varname=None):
        self.comment_model = Comment
        self.object_expr = object_expr
        self.as_varname = as_varname
    
    def render(self, context):
        qs = self.get_query_set(context)
        context[self.as_varname] = self.get_context_value_from_queryset(context, qs)
        return ''
    
    def get_query_set(self, context):
        qs = self.comment_model.objects.all()
        
        field_names = [f.name for f in self.comment_model._meta.fields]
        if 'is_public' in field_names:
            qs = qs.filter(is_public=True)
        if getattr(settings, 'COMMENTS_HIDE_REMOVED', True) and 'is_removed' in field_names:
            qs = qs.filter(is_removed=False)
        
        return qs

class CommentListNode(BaseCommentNode):
    """Insert a list of comments into the context."""
    def get_context_value_from_queryset(self, context, qs):
        return list(qs)

class CommentCountNode(BaseCommentNode):
    """Insert a count of comments into the context."""
    def get_context_value_from_queryset(self, context, qs):
        return qs.count()

@register.tag
def get_comment_count(parser, token):
    return CommentCountNode.handle_token(parser, token)

@register.tag
def get_comment_list(parser, token):
    return CommentListNode.handle_token(parser, token)