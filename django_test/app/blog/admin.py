from django.contrib import admin
from .models import *


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    model = User


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    model = Comment
    list_display = ('content', 'is_active', 'article_id', 'author_id', 'created', 'modified')
    list_filter = ('is_active', 'created', 'modified')
    search_fields = ('article_id', 'author_id', 'created', 'modified')
    actions = ['approve_comments']

    def approve_comments(self, request, queryset):
        queryset.update(is_active=True)


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'creation_date', 'rating', 'created', 'modified')
    list_filter = ('type',)
    search_fields = ('title', 'description', 'id')
