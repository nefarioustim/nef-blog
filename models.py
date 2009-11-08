import re
from datetime import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.comments.models import Comment
from django.db import models

from BeautifulSoup import BeautifulSoup, Comment as BSComment

COMMENT_MAX_LENGTH = getattr(settings, 'COMMENT_MAX_LENGTH', 3000)

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
    
    def save(self, force_insert=False, force_update=False):
        self.body = sanitise(self.body)
        if self.excerpt:
            self.excerpt = sanitise(self.excerpt)
        super(Post, self).save(force_insert, force_update)

class Comment(models.Model):
    user_name = models.CharField(max_length=50)
    user_email = models.EmailField()
    user_url = models.URLField(blank=True)
    comment = models.TextField(max_length=COMMENT_MAX_LENGTH)
    
    # Metadata
    post = models.ForeignKey(Post)
    submit_date = models.DateTimeField(default=datetime.now)
    ip_address = models.IPAddressField(blank=True, null=True)
    is_public = models.BooleanField(default=True)
    is_removed = models.BooleanField(default=False)

def sanitise(value):
    whitelist = [
        'a:title:href', 'abbr:title', 'acronym:title', 'address',
        'blockquote:cite', 'br', 'caption', 'center', 'cite:url', 'code',
        'dd', 'del:cite:datetime', 'dfn', 'dl', 'dt', 'em', 'h1:id', 'h2:id',
        'h3:id', 'h4:id', 'h5:id', 'h6:id', 'hr', 'img:src:alt:width:height',
        'ins:cite:datetime', 'kbd', 'li', 'ol', 'p', 'pre', 'q:cite', 'samp',
        'strong', 'sub', 'sup', 'table', 'tbody', 'td', 'tfoot', 'th', 'thead',
        'tr', 'ul', 'var',
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