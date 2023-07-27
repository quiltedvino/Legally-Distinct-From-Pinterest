from django.contrib import admin
from .models import Comment
# Register your models here.


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['poster', 'content', 'target', 'created']
    list_filter = ['created']
    search_fields = ['content']
# Register your models here.
