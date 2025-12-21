from django.urls import path, reverse_lazy
from . import views
from django.contrib.auth import views as auth_views

app_name = 'blog'

urlpatterns = [
    path('', views.PostListView.as_view(), name='index'),
    path('posts/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
    path('category/<slug:category_slug>/',
         views.CategoryPostListView.as_view(), 
         name='category_posts'),
    path('create/', views.PostCreateView.as_view(), name='create_post'),
    path('posts/<int:pk>/edit/', views.PostUpdateView.as_view(), name='edit_post'),
    path('posts/<int:pk>/delete/', views.PostDeleteView.as_view(), name='delete_post'),
    path('profile/<str:username>/', views.ProfileView.as_view(), name='profile'),
    path('posts/<int:pk>/comment/', views.CommentCreateView.as_view(), name='add_comment'),
    path('profile/edit/', views.EditProfileView.as_view(), name='edit_profile'),
    path('profile/password_change/',
        auth_views.PasswordChangeView.as_view(
            template_name='registration/password_change_form.html',
            success_url=reverse_lazy('blog:index') 
        ),
        name='password_change'),
    path('posts/<int:post_pk>/edit_comment/<int:pk>/', 
         views.CommentUpdateView.as_view(), name='edit_comment'),
    path('posts/<int:post_pk>/delete_comment/<int:pk>/', 
         views.CommentDeleteView.as_view(), name='delete_comment'),
]