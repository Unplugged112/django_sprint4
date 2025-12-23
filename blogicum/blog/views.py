from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.http import Http404
from blog.models import Post, Category, Comment
from blog.forms import PostForm, CommentForm, UserForm
from django.utils import timezone
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView, DetailView
) 
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.db.models import Q
from blog.utils import get_posts_with_comments, get_paginated_page


class PostMixin:
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'


class PostCreateView(LoginRequiredMixin, PostMixin, CreateView):
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.request.user.username})


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, PostMixin, UpdateView):
    def test_func(self):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, pk=post_id)
        return self.request.user == post.author
    
    def get_object(self, queryset=None):
        post_id = self.kwargs.get('post_id')
        return get_object_or_404(Post, pk=post_id)
    
    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.object.pk})


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = "blog/create.html"
    
    def get_object(self, queryset=None):
        post_id = self.kwargs.get('post_id')
        return get_object_or_404(Post, pk=post_id)
    
    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.request.user.username})


class PostDetailView(DetailView):
    model = Post
    template_name = "blog/detail.html"
    
    def get_object(self, queryset=None):
        post_id = self.kwargs.get('post_id')
        obj = get_object_or_404(Post, pk=post_id)
        user = self.request.user

        if obj.author == user:
            return obj

        if (obj.is_published and 
            obj.pub_date <= timezone.now() and 
            obj.category and 
            obj.category.is_published):
            return obj

        raise Http404("Пост недоступен")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.select_related('author')
        return context


class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = 10

    def get_queryset(self):
        base_queryset = Post.objects.select_related('category', 'author', 'location')
        
        return get_posts_with_comments(
            queryset=base_queryset,
            user=self.request.user,
            filter_published=True 
        )


class CategoryPostListView(ListView):
    model = Post
    template_name = 'blog/category.html'
    context_object_name = 'post_list'
    paginate_by = 10
    
    def get_queryset(self):        
        self.category = get_object_or_404(
            Category.objects.filter(is_published=True),
            slug=self.kwargs['category_slug']
        )
        
        base_queryset = Post.objects.select_related('author', 'location')
        
        additional_filters = Q(category=self.category)
        
        return get_posts_with_comments(
            queryset=base_queryset,
            user=self.request.user,
            filter_published=True,
            additional_filters=additional_filters
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class CommentCreateView(LoginRequiredMixin, CreateView):
    target_post = None
    template_name = 'blog/comment.html'
    model = Comment
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        self.target_post = get_object_or_404(Post, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.target_post
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.target_post.pk})


class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Comment
    template_name = 'blog/comment.html'
    form_class = CommentForm
    
    def get_object(self, queryset=None):
        comment_id = self.kwargs.get('comment_id')
        return get_object_or_404(Comment, pk=comment_id)

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author
    
    def get_success_url(self):
        comment = self.get_object()
        return reverse('blog:post_detail', kwargs={'post_id': comment.post.pk})


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'
    
    def get_object(self, queryset=None):
        comment_id = self.kwargs.get('comment_id')
        return get_object_or_404(Comment, pk=comment_id)

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author

    def get_success_url(self):
        comment = self.get_object()
        return reverse('blog:post_detail', kwargs={'post_id': comment.post.pk})


class ProfileView(DetailView): 
    model = User
    template_name = 'blog/profile.html'
    context_object_name = 'profile'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        base_queryset = Post.objects.filter(author=self.object)
        filter_published = (user != self.object)

        posts = get_posts_with_comments(
            queryset=base_queryset,
            user=user if filter_published else None,
            filter_published=filter_published
        )

        page_obj = get_paginated_page(
            objects=posts.order_by('-pub_date'),
            request=self.request,
            per_page=10
        )
        
        context['page_obj'] = page_obj
        return context


class EditProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return self.request.user
    
    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.object.username})