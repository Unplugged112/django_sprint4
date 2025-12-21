from blog.models import Category, Location, Post, Comment
from django.contrib import admin


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
	pass

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
	pass

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
	pass

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
	pass