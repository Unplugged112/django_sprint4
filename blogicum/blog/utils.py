from django.db.models import Count
from blog.models import Post
from django.db.models import Q

def get_most_commented_posts(queryset=None):
    if queryset is None:
        queryset = Post.objects.all()
    return queryset.annotate(
        comment_count=Count('comments', filter=Q(comments__isnull=False))
    ).order_by('-pub_date')