from django.db import models
from django.contrib.auth.models import User
from django.utils.html import mark_safe
from markdown import markdown

class Question(models.Model):
    class Meta:
        verbose_name = '主题'
        verbose_name_plural = '主题'
    
    user = models.ForeignKey(User,on_delete=models.CASCADE,default=1,verbose_name='作者')
    question_title = models.CharField(max_length=40,verbose_name='标题')
    question_text = models.TextField(max_length=9999,default="",verbose_name='内容')
    pub_date = models.DateTimeField(auto_now_add=True,verbose_name='时间')
    picture = models.FileField(blank=True,null=True)
    def __str__(self):
        return str(self.user) +":"+ self.question_title

    def get_text_to_md(self):
        return mark_safe(markdown(self.question_text))


class Choice(models.Model):
    class Meta:
        verbose_name = '评论'
        verbose_name_plural = '评论'
    
    choice_text = models.CharField(max_length=200,verbose_name='评论')
    user = models.ForeignKey(User,on_delete=models.CASCADE,default=1,verbose_name='作者')
    question = models.ForeignKey(Question, on_delete=models.CASCADE,verbose_name='主题')
    picture = models.FileField(blank=True,null=True)
    def __str__(self):
        return str(self.user)+":"+ self.choice_text
    
    def get_text_to_md(self):
        return mark_safe(markdown(self.choice_text))
    
