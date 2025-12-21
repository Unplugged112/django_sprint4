from django import forms
from .models import Post, Comment
from django.contrib.auth.models import User


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'text', 'pub_date', 'author', 'category', 'location', 'is_published', 'image']
        widgets = {
            'pub_date': forms.DateTimeInput(attrs={'type': 'date'}),
        }

    def clean_pub_date(self):
        pub_date = self.cleaned_data['pub_date']
        return pub_date
	
        
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']