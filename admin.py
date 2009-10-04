from django.contrib import admin

from nefariousdesigns.blog.models import Category, Post

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
	
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'pub_date', 'status')
    prepopulated_fields = {"slug": ("title",)}
    
    fieldsets = [
        (None, {
            'fields': ['title', 'excerpt', 'body']
        }),
        ('Date Information', {
            'fields': ['pub_date'],
            'classes': ['collapse']
        }),
        ('Categorisation', {
            'fields': ['categories']
        }),
        ('Metadata', {
            'fields': ['status', 'author', 'enable_comments', 'slug']
        }),
        ('SEO', {
            'fields': ['meta_keywords', 'meta_description']
        })
    ]

admin.site.register(Category, CategoryAdmin)
admin.site.register(Post, PostAdmin)