from django import forms
from simpleblog.models import Category


class BlogForm(forms.Form):
    """docstring for BlogForm"""
    caption = forms.CharField(label='title', max_length=100, required=True)
    content = forms.CharField(widget=forms.Textarea, required=True)


class TagForm(forms.Form):
    """docstring for TagForm"""
    tag_name = forms.CharField()


class CategoryForm(forms.Form):
    category_name = forms.ChoiceField(choices=[(o.id, o.category_name) for o in Category.objects.filter(depth=2)])


class WeiboForm(forms.Form):
    """docstring for WeiboForm"""
    massage = forms.CharField(widget=forms.Textarea)

