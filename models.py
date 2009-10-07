import re
from datetime import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.comments.models import Comment
from django.contrib.sites.models import Site
from django.core.mail import mail_managers
from django.db import models
from django.db.models.signals import pre_save
from django.utils.encoding import smart_str

from akismet import Akismet
from BeautifulSoup import BeautifulSoup, Comment as BSComment

class Category(models.Model):
    """Blog post category.
    
    Used for organisation of blog posts against keywords.
    
    Has a many-to-many relationship with the Post model.
    
    """
    
    title = models.CharField(max_length=250,
                             help_text='Maximum 250 characters.')
    slug = models.SlugField(unique=True,
                            help_text='Suggested value automatically \
                            generated from title. Must be unique.')
    
    class Meta:
        ordering = ['title']
        verbose_name_plural = "Categories"
    
    def __unicode__(self):
        return self.title
    
    def get_absolute_url(self):
        return '/%s/' % self.slug
    
    def pub_post_set(self):
        return self.post_set.filter(status=Post.STATUS_PUB)

class PubPostManager(models.Manager):
    def get_query_set(self):
        return super(PubPostManager, self).get_query_set().filter(status=self.model.STATUS_PUB)

class Post(models.Model):
    """Blog post.
    
    Stores blog post text and metadata.
    
    Has a many-to-many relationship with the Category model.
    
    """
    
    # Constants
    STATUS_PUB = 1
    STATUS_DRAFT = 2
    STATUS_CHOICES = (
        (STATUS_PUB, 'Published'),
        (STATUS_DRAFT, 'Draft'),
    )
    
    objects = models.Manager()
    pub = PubPostManager()
    
    # Core fields
    title = models.CharField(max_length=250,
                             help_text='Maximum 250 characters.')
    excerpt = models.TextField(blank=True)
    body = models.TextField()
    pub_date = models.DateTimeField(default=datetime.now)
    
    # Categorisation fields
    categories = models.ManyToManyField(Category)
    
    # Metadata fields
    author = models.ForeignKey(User)
    enable_comments = models.BooleanField(default=True)
    slug = models.SlugField(unique=True,
                            help_text='Suggested value automatically \
                            generated from title. Must be unique.')
    status = models.IntegerField(choices=STATUS_CHOICES, default=STATUS_DRAFT,
                                 help_text="Only entries with 'Published' \
                                 status will be publicly displayed.")
    
    # SEO fields
    meta_keywords = models.CharField(blank=True, max_length=250,
                                     help_text='Maximum 250 characters.')
    meta_description = models.CharField(blank=True, max_length=250,
                                        help_text='Maximum 250 characters.')
    
    class Meta:
        ordering = ['-pub_date']
    
    def __unicode__(self):
        return self.title
    
    def get_absolute_url(self):
        return '/%s.html' % self.slug

def sanitise(value):
    whitelist = [
        'a:title:href', 'abbr:title', 'acronym:title', 'address',
        'blockquote:cite', 'br', 'caption', 'center', 'cite:url', 'code',
        'dd', 'del:cite:datetime', 'dfn', 'dl', 'dt', 'em', 'h1', 'h2', 'h3',
        'h4', 'h5', 'h6', 'hr', 'img:src:alt', 'ins:cite:datetime', 'kbd',
        'li', 'ol', 'p', 'pre', 'q:cite', 'samp', 'strong', 'sub', 'sup',
        'table', 'tbody', 'td', 'tfoot', 'th', 'thead', 'tr', 'ul', 'var',
    ]
    
    js_regex = re.compile(r'[\s]*(&#x.{1,7})?'.join(list('javascript')))
    allowed_tags = [tag.split(':') for tag in whitelist]
    allowed_tags = dict((tag[0], tag[1:]) for tag in allowed_tags)
    
    soup = BeautifulSoup(value)
    for comment in soup.findAll(text=lambda text: isinstance(text, BSComment)):
        comment.extract()
    
    for tag in soup.findAll(True):
        if tag.name not in allowed_tags:
            tag.hidden = True
        else:
            tag.attrs = [(attr, js_regex.sub('', val)) for attr, val in tag.attrs
                         if attr in allowed_tags[tag.name]]
    
    return soup.renderContents().decode('utf8')

def moderate_comment(sender, **kwargs):
    """Comment moderation callback function.
    
    Registered against django.contrib.comments comment pre_save.
    
    """
    
    instance = kwargs["instance"]
    
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
    
    email_body = "%s posted a new comment on the entry '%s'."
    mail_managers("New comment posted", email_body %
                  (instance.user_name, instance.content_object))

pre_save.connect(moderate_comment, sender=Comment)