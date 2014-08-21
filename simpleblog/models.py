#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User

class Tag(models.Model):
    """docstring for Tags"""
    tag_name = models.CharField(max_length=20)
    create_time = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.tag_name


class BlogManager(models.Manager):
    """docstring for BlogManager"""
    def title_count(self, keyword):
        return self.filter(caption__icontains=keyword).count()

    def tag_count(self, keyword):
        return self.filter(tags__icontains=keyword).count()


class AbstractCategory(models.Model):
    parent = models.ForeignKey('self',blank=True, null=True, related_name='children')
    class Meta:
        abstract = True

class Category(AbstractCategory):
    """category manage of blogs"""
    category_name = models.CharField(max_length=20)
    sort = models.IntegerField(default=0, blank=True)
    visible = models.BooleanField(default=False, blank=True)
    add_time = models.DateTimeField(auto_now_add=True)
    depth = models.IntegerField(blank=True, default=1)

    def __unicode__(self):
        return self.category_name


class Blog(models.Model):
    """docstring for Blogs"""
    caption = models.CharField(max_length=50)
    author = models.ForeignKey(User)
    tags = models.ManyToManyField(Tag, blank=True)
    category = models.ForeignKey(Category)
    content = models.TextField()
    publish_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    objects = models.Manager()
    count_objects = BlogManager()
    taglist = []

    def save(self, *args, **kwargs):
        super(Blog, self).save()
        for i in self.taglist:
            p, created = Tag.objects.get_or_create(tag_name=i)
            self.tags.add(p)

    def __unicode__(self):
        return u'%s %s %s' % (self.caption, self.author, self.publish_time)


class Weibo(models.Model):
    massage = models.CharField(max_length=200)
    author = models.ForeignKey(User)
    publish_time = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.massage
