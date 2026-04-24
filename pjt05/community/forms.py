from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 3,
                'placeholder': '댓글을 남겨보세요...',
                'style': 'min-height: 80px;'
            }),
        }
        labels = {
            'content': '',
        }
