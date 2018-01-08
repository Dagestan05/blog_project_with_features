from django.contrib import admin
from posts.models import Post
# Register your models here.

class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'updated', 'timestamp']
    list_display_links = ['updated']
    list_filter = ['updated', 'timestamp']
    search_fields = ['title', 'content']
    list_editable = ['title']
    class Meta:
        model = Post


admin.site.register(Post, PostAdmin)


