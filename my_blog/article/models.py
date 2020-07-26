from django.db import models
#导入内建的User模型
from django.contrib.auth.models import User
#timezone 用于处理时间相关事务
from django.utils import timezone
from django.urls import reverse
# Django-taggit
from taggit.managers import TaggableManager
from PIL import Image
from DjangoUeditor.models import UEditorField
# Create your models here.

class ArticleColumn(models.Model):
    """
    栏目的 Model
    """
    # 栏目标题
    title = models.CharField(max_length=100, blank=True)
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

#博客文章数据模型
class ArticlePost(models.Model):
    #文章作者，参数on_delete用于指定数据删除方式
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    #文章标题。models.CharField 为字符串字段，用于保存较短的字符串，比如标题
    title = models.CharField(max_length=100)

    # 文章正文。保存大量文本使用 TextField
    #body = models.TextField()
    body = UEditorField(imagePath='upload/', filePath='upload/', blank=True, width="100%", height=300)
    # 文章创建时间。参数 default=timezone.now 指定其在创建数据时将默认写入当前的时间
    created = models.DateTimeField(default=timezone.now)

    # 文章更新时间。参数 auto_now=True 指定每次数据更新时自动写入当前时间
    updated = models.DateTimeField(auto_now=True)
    #浏览量
    total_views = models.PositiveIntegerField(default=0)
    # 文章标题图
    avatar = models.ImageField(upload_to='article/%Y%m%d/', blank=True)

    # 新增点赞数统计
    likes = models.PositiveIntegerField(default=0)

    # 保存时处理图片
    def save(self, *args, **kwargs):
        # 调用原有的 save() 的功能
        article = super(ArticlePost, self).save(*args, **kwargs)
        # 固定宽度缩放图片大小
        if self.avatar and not kwargs.get('update_fields'):
            image = Image.open(self.avatar)
            (x, y) = image.size
            new_x = 80
            new_y = int(new_x * (y / x))
            resized_image = image.resize((new_x, new_y), Image.ANTIALIAS)
            resized_image.save(self.avatar.path)
        return article
    # 文章标签
    tags = TaggableManager(blank=True)

    def get_tags(self):
        return self.tags.names()

    # 文章栏目的 “一对多” 外键
    column = models.ForeignKey(
        ArticleColumn,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='article',
    )

    # 获取文章地址
    def get_absolute_url(self):
        return reverse('article:detail_view', args=[self.pk])
    # 内部类 class Meta 用于给 model 定义元数据
    class Meta:
        # ordering 指定模型返回的数据的排列顺序
        # '-created' 表明数据应该以倒序排列
        ordering = ('-created',)

    # 函数 __str__ 定义当调用对象的 str() 方法时的返回值内容
    def __str__(self):
        # return self.title 将文章标题返回
        return self.title

    def was_created_recently(self):
        diff = timezone.now() - self.created
        if diff.days == 0 and diff.seconds >= 0 and diff.seconds < 60:
            return True
        else:
            return False


