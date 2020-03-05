from django.shortcuts import render

# 导入 HttpResponse 模块
from django.shortcuts import render

# Create your views here.
# 导入数据模型ArticlePost
from .models import ArticlePost
import markdown

# 引入redirect重定向模块
from django.shortcuts import render, redirect
# 引入HttpResponse
from django.http import HttpResponse
# 引入刚才定义的ArticlePostForm表单类
from .forms import ArticlePostForm
# 引入User模型
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
# 引入分页模块
from django.core.paginator import Paginator
# 引入 Q 对象
from django.db.models import Q
from comment.models import Comment
# 引入栏目Model
from .models import ArticleColumn
# 引入评论表单
from comment.forms import CommentForm
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView

class ArticleListView(ListView):
    context_object_name = 'articles'
    template_name = 'article/list.html'
    obj = ''
    def get_queryset(self):
        queryset = ArticlePost.objects.all()
        return queryset

    def get_context_data(self, **kwargs):
        article_new = ArticlePost.objects.all().order_by('-id')[:3]
        article_views = ArticlePost.objects.all().order_by('-total_views')[:3]
        paginator = Paginator(self.get_queryset(), 3)
        page = self.request.GET.get('page')
        articles = paginator.get_page(page)
        context = {
            'articles': articles,
            'article_new': article_new,
            'article_views': article_views,
        }
        kwargs.update(context)
        return super(ArticleListView, self).get_context_data(**kwargs)

class IndexView(ArticleListView):
    template_name = 'index.html'

#文章详情
class ArticleDetailView(DetailView):
    queryset = ArticlePost.objects.all().order_by("-updated")
    context_object_name = 'article'
    template_name = 'article/detail.html'
    def get_object(self):
        obj = super(ArticleDetailView, self).get_object()
        obj.total_views += 1
        obj.save(update_fields=['total_views'])
        md = markdown.Markdown(
            extensions=[
                # 包含 缩写、表格等常用扩展
                'markdown.extensions.extra',
                # 语法高亮扩展
                'markdown.extensions.codehilite',
                # 目录扩展
                # 'markdown.extensions.toc',
            ]
        )
        obj.body = md.convert(obj.body)
        return obj
    def get_context_data(self, **kwargs):
        comment_form = CommentForm()
        article_id = self.kwargs.get('pk')
        comments = Comment.objects.filter(article=article_id)
        context = {
            'comments_form': comment_form,
            'comments': comments,
        }
        kwargs.update(context)
        return super(ArticleDetailView, self).get_context_data(**kwargs)

# 写文章的视图
# 检查登录
"""
@login_required(login_url='/userprofile/login/')
def article_create(request):
    # 判断用户是否提交数据
    if request.method == 'POST':
        # 将提交的数据赋值到表单实例中
        article_post_form = ArticlePostForm(request.POST, request.FILES)
        # 判断提交的数据是否满足模型的要求
        if article_post_form.is_valid():
            # 保存数据，但暂时不提交到数据库中
            new_article = article_post_form.save(commit=False)
            # 指定数据库中 id=1 的用户为作者
            # 如果你进行过删除数据表的操作，可能会找不到id=1的用户
            # 此时请重新创建用户，并传入此用户的id
            new_article.author = User.objects.get(id=request.user.id)
            # 将新文章保存到数据库中

            if request.POST['column'] != 'none':
                new_article.column = ArticleColumn.objects.get(id=request.POST['column'])
            new_article.save()
            #保存 tags 的多对多关系
            article_post_form.save_m2m()
            # 完成后返回到文章列表
            return redirect("article:list_view")
        # 如果数据不合法，返回错误信息
        else:
            return HttpResponse("表单内容有误，请重新填写。")
    # 如果用户请求获取数据
    else:
        # 创建表单类实例
        article_post_form = ArticlePostForm()
        columns = ArticleColumn.objects.all()
        # 赋值上下文
        context = { 'article_post_form': article_post_form, 'columns': columns}
        # 返回模板
        return render(request, 'article/create.html', context)
"""

class ArticleCreateView(CreateView):
    model = ArticlePost
    fields = '__all__'
    template_name = 'article/create.html'

# 删文章
# 检查登录
@login_required(login_url='/userprofile/login/')
def article_delete(request, id):
    # 根据 id 获取需要删除的文章
    article = ArticlePost.objects.get(id=id)
    # 过滤非作者的用户
    if request.user != article.author:
        return HttpResponse("抱歉，你无权删除这篇文章。")
    # 调用.delete()方法删除文章
    article.delete()
    # 完成删除后返回文章列表
    return redirect("article:list_view")

# 安全删除文章
# 检查登录
@login_required(login_url='/userprofile/login/')
def article_safe_delete(request, id):
    # 过滤非作者的用户
    if request.user != article.author:
        return HttpResponse("抱歉，你无权删除这篇文章。")
    if request.method == 'POST':
        article = ArticlePost.objects.get(id=id)
        article.delete()
        return redirect("article:list_view")
    else:
        return HttpResponse("仅允许post请求")

# 更新文章
# 检查登录
@login_required(login_url='/userprofile/login/')
def article_update(request, id):
    """
    更新文章的视图函数
    通过POST方法提交表单，更新titile、body字段
    GET方法进入初始表单页面
    id： 文章的 id
    """
    # 获取需要修改的具体文章对象
    article = ArticlePost.objects.get(id=id)
    # 过滤非作者的用户
    if request.user != article.author:
        return HttpResponse("抱歉，你无权修改这篇文章。")
    if request.method == 'POST':
        # 将提交的数据赋值到表单实例中
        article_post_form = ArticlePostForm(data=request.POST)
        # 判断提交的数据是否满足模型的要求
        if article_post_form.is_valid():
            # 保存新写入的 title、body 数据并保存
            article.title = request.POST['title']
            article.body = request.POST['body']
            if request.POST['column'] != 'none':
                article.column = ArticleColumn.objects.get(id=request.POST['column'])
            else:
                article.column = None
            if request.FILES.get('avatar'):
                article.avatar = request.FILES.get('avatar')
            article.tags.set(*request.POST.get('tags').split(','), clear=True)
            article.save()
            # 完成后返回到修改后的文章中。需传入文章的 id 值
            return redirect("article:detail_view", pk=id)
        # 如果数据不合法，返回错误信息
        else:
            return HttpResponse("表单内容有误，请重新填写。")
    # 如果用户 GET 请求获取数据
    else:
        # 创建表单类实例
        article_post_form = ArticlePostForm()
        columns = ArticleColumn.objects.all()
        # 赋值上下文，将 article 文章对象也传递进去，以便提取旧的内容
        context = {
            'article': article,
            'article_post_form': article_post_form,
            'columns': columns,
            'tags': ','.join([x for x in article.tags.names()]),

        }
        # 将响应返回到模板中
        return render(request, 'article/update.html', context)

#点赞数 +1
class IncreaseLinkesView(View):
    def post(self, request, *args, **kwargs):
        article = ArticlePost.objects.get(id=kwargs.get('id'))
        article.likes += 1
        article.save()
        return HttpResponse('success')

