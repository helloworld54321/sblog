# -*- coding: utf-8 -*-

from django.contrib import auth
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.contrib import messages

from accounts.forms import LoginForm, RegisterForm


def home(request):
    '''用户中心'''
    if request.user.is_authenticated():
        user = request.user;
    else:
        user = request.user;
    return render_to_response('accounts/home.html',{'user':user},context_instance=RequestContext(request));

def regist(request):
    '''用户注册页'''
    form = RegisterForm()
    if request.method=="POST":
        form=RegisterForm(request.POST.copy())
        if form.is_valid():
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            repassword = form.cleaned_data["repassword"]
            print form
            if password != repassword:
                return HttpResponse('重复登录密码与登录密码不一致');
            user = User.objects.create_user(username, email, password)
            user.save()
            validate_login(request, username, password)
            return HttpResponseRedirect("/simpleblog/bloglist")
    return render_to_response('accounts/register.html',{'form':form},context_instance=RequestContext(request));


def register_check(request):
    if request.method == "POST":
        username = request.POST.get('username')
        if User.objects.filter(username = username).exists():
            return HttpResponse('0')
        else:
            return HttpResponse('1')

def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/simpleblog/bloglist')


def login(request):
    if request.method == 'GET':
        form = LoginForm()
        return render_to_response('login.html', RequestContext(request, {'form': form}))
    else:
        print "in post"
        form = LoginForm(request.POST)
        if form.is_valid():
            result = validate_login(request, form.cleaned_data["username"], form.cleaned_data["password"])
            if result:
                return HttpResponseRedirect("/simpleblog/bloglist")
            else:
                return render_to_response('login.html', RequestContext(request, {'form': form ,'password_is_wrong':True}))
        else:
            return render_to_response('login.html', RequestContext(request, {'form': form}))


def validate_login(request, username, password):
    '''验证用户登录'''
    return_value = False
    user = auth.authenticate(username=username,password=password)
    if user:
        if  user.is_active:
            auth.login(request,user)
            return_value = True
        else:
            messages.addmessage(request, messages.INFO, '此账户尚未激活，请联系管理员')
    else:
        messages.add_message(request, messages.INFO, '此账户不存在，请联管理员')

    return return_value
