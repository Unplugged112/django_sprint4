from django.urls import path, reverse_lazy
from . import views
from django.contrib.auth import views as auth_views

app_name = 'blog'

urlpatterns = [
    path('', views.PostListView.as_view(), name='index'),
    
    # Для постов
    path('posts/<int:post_id>/', views.PostDetailView.as_view(), name='post_detail'),
    path('posts/<int:post_id>/edit/', views.PostUpdateView.as_view(), name='edit_post'),
    path('posts/<int:post_id>/delete/', views.PostDeleteView.as_view(), name='delete_post'),
    path('posts/<int:post_id>/comment/', views.CommentCreateView.as_view(), name='add_comment'),
    
    # Для комментариев
    path('posts/<int:post_id>/comments/<int:comment_id>/edit/', 
         views.CommentUpdateView.as_view(), name='edit_comment'),
    path('posts/<int:post_id>/comments/<int:comment_id>/delete/', 
         views.CommentUpdateView.as_view(), name='delete_comment'),
    
    # Для категорий и профилей
    path('category/<slug:category_slug>/',
         views.CategoryPostListView.as_view(), 
         name='category_posts'),
    path('profile/edit/', views.EditProfileView.as_view(), name='edit_profile'),
    path('profile/<str:username>/', views.ProfileView.as_view(), name='profile'),

    
    # Создание поста
    path('create/', views.PostCreateView.as_view(), name='create_post'),
    
    # Аутентификация
    path('profile/password_change/',
        auth_views.PasswordChangeView.as_view(
            template_name='registration/password_change_form.html',
            success_url=reverse_lazy('blog:index') 
        ),
        name='password_change'),
]