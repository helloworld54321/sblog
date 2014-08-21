from django.shortcuts import render_to_response
from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.core.context_processors import csrf
from simpleblog.forms import BlogForm
from simpleblog.forms import TagForm
from simpleblog.forms import CategoryForm
from simpleblog.models import Blog, Category
from simpleblog.models import Tag
from simpleblog.models import Weibo
from simpleblog.models import Category
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, InvalidPage, EmptyPage


def blog_list(request):
    blog_list = Blog.objects.order_by('-publish_time')
    setBlogAbstract(blog_list)
    paginator = Paginator(blog_list, 25)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        blogs = paginator.page(page)
    except (EmptyPage, InvalidPage):
        blogs = paginator.page(paginator.num_pages)
    tags = Tag.objects.all()
    weibos = Weibo.objects.order_by('-publish_time')[:5]
    treeList = load_category_tree()
    return render_to_response("blog_list.html",
                              {"blogs": blogs, "tags": tags, "weibos": weibos, "treeList": treeList},
                              context_instance=RequestContext(request))


def load_category_tree():
    cs = Category.objects.filter(parent=None).order_by('-sort')
    print  cs
    treeList = []
    for c in cs:
        tmpDict = {}
        tmpDict['category_name'] = c.category_name
        tmpDict['id'] = c.id
        tmpDict['children'] = list(Category.objects.filter(parent=c.id).order_by('-sort'))
        print tmpDict
        treeList.append(tmpDict)
    return treeList


def blog_filter(request, id=''):
    tags = Tag.objects.all()
    tag = Tag.objects.get(id=id)
    blogs = tag.blog_set.all()
    setBlogAbstract(blogs)
    treeList = load_category_tree()
    return render_to_response("blog_filter.html",
                              {"blogs": blogs, "tag": tag, "tags": tags,"treeList":treeList})

def blog_category_filter(request,id=''):
    treeList = load_category_tree()
    blogs=Blog.objects.filter(category_id=id)
    setBlogAbstract(blogs)
    return render_to_response("blog_filter.html",
            {"blogs": blogs,"treeList":treeList})

def blog_search(request):
    tags = Tag.objects.all()
    if 'search' in request.GET:
        search = request.GET['search']
        blogs = Blog.objects.filter(caption__icontains=search)
        return render_to_response('blog_filter.html',
                                  {"blogs": blogs, "tags": tags}, context_instance=RequestContext(request))
    else:
        blogs = Blog.objects.order_by('-id')
        return render_to_response("blog_list.html", {"blogs": blogs, "tags": tags},
                                  context_instance=RequestContext(request))


def blog_show(request, id=''):
    try:
        blog = Blog.objects.get(id=id)
        tags = Tag.objects.all()
    except Blog.DoesNotExist:
        raise Http404
    return render_to_response("blog_show.html",
                              {"blog": blog, "tags": tags},
                              context_instance=RequestContext(request))


def blog_show_comment(request, id=''):
    blog = Blog.objects.get(id=id)
    return render_to_response('blog_comments_show.html', {"blog": blog})


def blog_del(request, id=""):
    try:
        blog = Blog.objects.get(id=id)
    except Exception:
        raise Http404
    if blog:
        blog.delete()
        return HttpResponseRedirect("/simpleblog/bloglist/")
    blogs = Blog.objects.all()
    return render_to_response("blog_list.html", {"blogs": blogs})


@login_required
def blog_add(request):
    if request.method == 'POST':
        form = BlogForm(request.POST)
        tag = TagForm(request.POST)
        categoryfrom = CategoryForm(request.POST)

        print categoryfrom
        if form.is_valid() and tag.is_valid() and categoryfrom.is_valid():
            cd = form.cleaned_data
            cdtag = tag.cleaned_data
            cd_category =categoryfrom.cleaned_data
            category_id=cd_category['category_name']
            tagname = cdtag['tag_name']
            for taglist in tagname.split():
                Tag.objects.get_or_create(tag_name=taglist.strip())

            title = cd['caption']
            author = request.user
            category = Category.objects.filter(id=category_id)[0]
            content = cd['content']
            blog = Blog(caption=title, author=author, content=content, category=category)
            blog.save()
            for taglist in tagname.split():
                blog.tags.add(Tag.objects.get(tag_name=taglist.strip()))
                blog.save()
            id = Blog.objects.order_by('-id')[0].id
            return HttpResponseRedirect('/simpleblog/blog/%s' % id)
    else:
        form = BlogForm()
        tag = TagForm()
        category = CategoryForm()
    return render_to_response('blog_add.html',
                              {'form': form, 'tag': tag, 'category': category},
                              context_instance=RequestContext(request))


@login_required()
def show_weibo(request):
    weibos = Weibo.objects.order_by('-publish_time')[:5]
    return render_to_response("blog_twitter.html", {"weibos": weibos})



def add_weibo(request):
    c = {}
    c.update(csrf(request))
    if request.method == 'POST':
        massage = request.POST['twitter']
        author = request.User
        massage = Weibo(massage=massage, author=author)
        massage.save()
        weibos = Weibo.objects.order_by('-publish_time')[:5]
        return render_to_response("blog_twitter.html",
                                  {"weibos": weibos},
                                  context_instance=RequestContext(request))
    else:
        return HttpResponse('dddd')


@login_required()
def blog_update(request, id=""):
    id = id
    if request.method == 'POST':
        form = BlogForm(request.POST)
        tag = TagForm(request.POST)
        if form.is_valid() and tag.is_valid():
            cd = form.cleaned_data
            cdtag = tag.cleaned_data
            tagname = cdtag['tag_name']
            tagnamelist = tagname.split()
            for taglist in tagnamelist:
                Tag.objects.get_or_create(tag_name=taglist.strip())
            title = cd['caption']
            content = cd['content']
            blog = Blog.objects.get(id=id)
            if blog:
                blog.caption = title
                blog.content = content
                blog.save()
                for taglist in tagnamelist:
                    blog.tags.add(Tag.objects.get(tag_name=taglist.strip()))
                    blog.save()
                tags = blog.tags.all()
                for tagname in tags:
                    tagname = unicode(str(tagname), "utf-8")
                    if tagname not in tagnamelist:
                        notag = blog.tags.get(tag_name=tagname)
                        blog.tags.remove(notag)
            else:
                blog = Blog(caption=blog.caption, content=blog.content)
                blog.save()
            return HttpResponseRedirect('/simpleblog/blog/%s' % id)
    else:
        try:
            blog = Blog.objects.get(id=id)
        except Exception:
            raise Http404
        form = BlogForm(initial={'caption': blog.caption, 'content': blog.content}, auto_id=False)
        tags = blog.tags.all()
        if tags:
            taginit = ''
            for x in tags:
                taginit += str(x) + ' '
            tag = TagForm(initial={'tag_name': taginit})
        else:
            tag = TagForm()
    return render_to_response('blog_add.html',
                              {'blog': blog, 'form': form, 'id': id, 'tag': tag},
                              context_instance=RequestContext(request))


def setBlogAbstract(blogs):
    if not len(blogs):
        return
    else:
        for blog in blogs:
            if len(blog.content)>180:
                blog.content=blog.content[0:180]+"......"
            else:
                continue