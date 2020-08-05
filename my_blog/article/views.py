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

class ArticleListView(ListView):
    context_object_name = 'articles'
    template_name = 'article/list.html'
    def get_queryset(self):
        queryset = ArticlePost.objects.all().order_by('-updated')
        return queryset

    def get_context_data(self, **kwargs):
        article_new = ArticlePost.objects.all().order_by('-id')[:5]
        article_views = ArticlePost.objects.all().order_by('-total_views')[:5]
        search = self.request.GET.get('search')
        order = self.request.GET.get('order')
        tag = self.request.GET.get('tag')
        columns = ArticleColumn.objects.all()
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
                    Q(column__title=search)
                    # Q(body__icontains=search)
                )
        elif tag and tag != 'None':
            self.get_queryset = ArticlePost.objects.filter(
                Q(tags__name__in=[tag]) |
                Q(column__title=tag) |
                Q(title__icontains=tag)
            ).distinct()
        else:
            # 将 search 参数重置为空
            search = ''
            if order == 'total_views':
                self.get_queryset = ArticlePost.objects.all().order_by('-total_views')
            else:
                self.get_queryset = ArticlePost.objects.all().order_by('-updated')
        paginator = Paginator(self.get_queryset, 8)
        page = self.request.GET.get('page')
        articles = paginator.get_page(page)
        context = {
            'articles': articles,
            'article_new': article_new,
            'article_views': article_views,
            'columns': columns,
            'tag': tag,
        }
        kwargs.update(context)
        return super(ArticleListView, self).get_context_data(**kwargs)

class IndexView(ArticleListView):
    template_name = 'index.html'

class ArticleArchiveView(ListView):
    template_name = 'article/archive.html'
    def get_queryset(self):
        queryset = ArticlePost.objects.all().order_by('-created')
        return queryset
    def get_context_data(self, **kwargs):
        articles = self.get_queryset()
        context = {
            'articles': articles,
        }
        kwargs.update(context)
        return super(ArticleArchiveView, self).get_context_data(**kwargs)

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
        pre_article = ArticlePost.objects.filter(id__lt=article_id).order_by('-id')
        next_article = ArticlePost.objects.filter(id__gt=article_id).order_by('id')
        if pre_article.count() > 0:
            pre_article = pre_article[0]
        else:
            pre_article = None
        if next_article.count() > 0:
            next_article = next_article[0]
        else:
            next_article = None
        context = {
            'comments_form': comment_form,
            'comments': comments,
            'pre_article': pre_article,
            'next_article': next_article,
        }
        kwargs.update(context)
        return super(ArticleDetailView, self).get_context_data(**kwargs)

class ArticleCourseView(ArticleListView):
    template_name = 'course/course.html'

class ArticleCourseDetailView(ArticleDetailView):
    template_name = 'course/course_detail.html'

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




