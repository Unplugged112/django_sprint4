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
from blog.utils import get_most_commented_posts


class PostMixin:
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')


class PostCreateView(LoginRequiredMixin, PostMixin, CreateView):
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.request.user.username})


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, PostMixin, UpdateView):
    def test_func(self):
        return self.request.user == self.get_object().author
    
    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.object.pk})


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = "blog/create.html"

    def test_func(self):
        return self.request.user == self.get_object().author

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.request.user.username})


class PostDetailView(DetailView):
    model = Post
    template_name = "blog/detail.html"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
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
        current_time = timezone.now()
        user = self.request.user

        qs = Post.objects.select_related('category', 'author', 'location')

        base_filter = Q(
            pub_date__lte=current_time, 
            is_published=True, 
            category__is_published=True
        )

        if user.is_authenticated:
            qs = qs.filter(base_filter | Q(author=user))
        else:
            qs = qs.filter(base_filter)

        qs = get_most_commented_posts(qs)

        return qs


class CategoryPostListView(ListView):
    model = Post
    template_name = 'blog/category.html'
    context_object_name = 'post_list'
    paginate_by = 10
    
    def get_queryset(self):
        current_time = timezone.now()
        self.category = get_object_or_404(
            Category.objects.filter(is_published=True),
            slug=self.kwargs['category_slug']
        )
        return Post.objects.filter(
            category=self.category,
            is_published=True,
            pub_date__lte=current_time
        ).select_related('category', 'author', 'location')

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

    def test_func(self):
        return self.request.user == self.get_object().author
    
    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.object.post.pk})


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'

    def test_func(self):
        return self.request.user == self.get_object().author

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.object.post.pk})


class ProfileView(DetailView): 
    model = User
    template_name = 'blog/profile.html'
    context_object_name = 'profile'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        current_time = timezone.now()
        
        if user == self.object:  
            posts = Post.objects.filter(author=self.object)
        else: 
            posts = Post.objects.filter(
                author=self.object,
                is_published=True,
                category__is_published=True,
                pub_date__lte=current_time
            )
    
        from django.core.paginator import Paginator
        paginator = Paginator(posts.order_by('-pub_date'), 10)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
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