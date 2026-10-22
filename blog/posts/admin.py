from django.contrib import admin

from .models import Post

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'post_title', 'published_date')
    list_display_links = ('id', 'post_title')

# admin.site.register(Post, PostAdmin)