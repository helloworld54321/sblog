#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.conf.urls import *


urlpatterns = patterns(('accounts.views'),
    #url(r'^logout/$', 'logout'),
    url(r'^login/$', 'login'),
    url(r'^logout/$', 'logout'),
    url(r'^regist/$','regist')
)

