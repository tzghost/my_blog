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
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin

class ArticleListView(ListView):
    context_object_name = 'articles'
    template_name = 'article/list.html'
    obj = ''
    def get_queryset(self):
        queryset = ArticlePost.objects.all().order_by('-updated')
        return queryset

    def get_context_data(self, **kwargs):
        article_new = ArticlePost.objects.all().order_by('-id')[:3]
        article_views = ArticlePost.objects.all().order_by('-total_views')[:3]
        search = self.request.GET.get('search')
        order = self.request.GET.get('order')
        if search:
            if order == 'total_views':
                # 用 Q对象 进行联合搜索
                self.get_queryset = ArticlePost.objects.filter(
                    Q(title__icontains=search) |
                    Q(body__icontains=search)
                ).order_by('-total_views')
            else:
                self.get_queryset = ArticlePost.objects.filter(
                    Q(title__icontains=search) |
                    Q(body__icontains=search)
                )
        else:
            # 将 search 参数重置为空
            search = ''
            if order == 'total_views':
                self.get_queryset = ArticlePost.objects.all().order_by('-total_views')
            else:
                self.get_queryset = ArticlePost.objects.all()
        paginator = Paginator(self.get_queryset, 3)
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
class ArticleCreateView(LoginRequiredMixin, CreateView):
    model = ArticlePost
    template_name = 'article/create.html'
    form_class = ArticlePostForm
    success_url = 'article/list.html'
    def get_queryset(self):
        columns = ArticleColumn.objects.all()
        return columns
    def get_context_data(self, **kwargs):
        context = {
            'columns': self.get_queryset,
        }
        kwargs.update(context)
        return super(ArticleCreateView, self).get_context_data(**kwargs)

    def post(self, request, **kwargs):
        article_post_form = ArticlePostForm(request.POST, request.FILES)
        if article_post_form.is_valid():
            new_article = article_post_form.save(commit=False)
            new_article.author = User.objects.get(id=request.user.id)

            if request.POST['column'] != 'none':
                new_article.column = ArticleColumn.objects.get(id=request.POST['column'])
            new_article.save()

            article_post_form.save_m2m()
            return redirect("article:list_view")
        else:
            return HttpResponse("表单内容有误，请重新填写。")

class ArticleDeleteView(LoginRequiredMixin, DeleteView):
    model = ArticlePost
    pk_url_kwarg = 'pk'
    queryset = ArticlePost.objects.filter()
    success_url = reverse_lazy("article:list_view")

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

class ArticleUpdateView(LoginRequiredMixin, UpdateView):
    model = ArticlePost
    template_name = 'article/update.html'
    context_object_name = "obj"
    form_class = ArticlePostForm

    def post(self, request, **kwargs):
        article_post_form = ArticlePostForm(data=request.POST)
        article = ArticlePost.objects.get(id=self.kwargs.get('pk'))
        if article_post_form.is_valid():
            # 保存新写入的 title、body 数据并保存
            article.title = request.POST['title']
            article.body = request.POST['body']

            if request.POST['column'] != 'none':
                # 保存文章栏目
                article.column = ArticleColumn.objects.get(id=request.POST['column'])
            else:
                article.column = None

            if request.FILES.get('avatar'):
                article.avatar = request.FILES.get('avatar')

            article.tags.set(*request.POST.get('tags').split(','), clear=True)
            article.save()
            return redirect("article:detail_view", pk=self.kwargs.get('pk'))
        else:
            return HttpResponse("表单内容有误，请重新填写。")

    def get_context_data(self, **kwargs):
        context = {
            'article_post_form': self.form_class,
            'columns': ArticleColumn.objects.all(),
        }
        kwargs.update(context)
        return super(ArticleUpdateView, self).get_context_data(**kwargs)

#点赞数 +1
class IncreaseLinkesView(View):
    def post(self, request, *args, **kwargs):
        article = ArticlePost.objects.get(id=self.kwargs.get('pk'))
        article.likes += 1
        article.save()
        return HttpResponse('success')

