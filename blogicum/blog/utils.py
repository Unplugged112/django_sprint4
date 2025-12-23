# blog/utils.py
from django.utils import timezone
from django.db.models import Q, Count
from .models import Post
from django.core.paginator import Paginator


def get_posts_with_comments(queryset=None, user=None, filter_published=True, 
                           additional_filters=None, order_by='-pub_date'):
    if queryset is None:
        queryset = Post.objects.all()

    if filter_published:
        current_time = timezone.now()
        
        base_filter = Q(
            pub_date__lte=current_time,
            is_published=True,
            category__is_published=True
        )
        
        if additional_filters:
            base_filter = base_filter & additional_filters
        
        if user and user.is_authenticated:
            queryset = queryset.filter(base_filter | Q(author=user))
        else:
            queryset = queryset.filter(base_filter)
    else:
        if additional_filters:
            queryset = queryset.filter(additional_filters)
    
    queryset = queryset.annotate(
        comment_count=Count('comments')
    )

    if order_by is not None:
        queryset = queryset.order_by(order_by)
    else:
        queryset = queryset.order_by(*Post._meta.ordering)
    
    return queryset

def get_paginated_page(objects, request, per_page):
 
    paginator = Paginator(objects, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)