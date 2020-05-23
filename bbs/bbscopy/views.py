from django.shortcuts import render,get_object_or_404
from django.http import HttpResponse,Http404,HttpResponseRedirect
from django.urls import reverse

from .models import Question,Choice
from accounts.models import UserUpdate
from .forms import QuestionForm
from .forms import ChoiceForm
from django.db.models import Q

from django.contrib.auth.decorators import login_required
from django.views.generic import ListView,CreateView


# 论坛首页
def index(request):
    latest_bbscopy_list = Question.objects.order_by('-pub_date')
    
    query = request.GET.get('query')
    if query:
        latest_bbscopy_list = latest_bbscopy_list.filter(
            Q(question_title__icontains=query) | 
            Q(user__username__icontains=query) |
            Q(pub_date__icontains=query)
        ).distinct()

    questionform = QuestionForm()
    return render(request,'bbscopy/index.html',
    {'latest_bbscopy_list':latest_bbscopy_list,'questionform':questionform,'now_user':{'user':request.user,'is_login':request.user.is_authenticated},})


# 帖子详情
def detail(request,bbscopy_id):
    try:
        bbscopy = Question.objects.get(pk=bbscopy_id)
        choiceform = ChoiceForm()
        # 帖子作者的头像
        q_pic = UserUpdate.objects.get(user_id=bbscopy.user_id).picture
        # 评论人的头像
        u_pic_list = UserUpdate.objects.all()
        u_choice_list = bbscopy.choice_set.all()
        u_to_p_dict = {}
        for u in u_choice_list:
            u_to_p_dict[u.user_id] = u_pic_list.get(user_id=u.user_id).picture
            
    except Question.DoesNotExist:
        raise Http404("这个帖子的id不存在！")
    return render(request, 'bbscopy/detail.html', 
    {'q_pic':q_pic,'u_to_p_dict':u_to_p_dict,'bbscopy': bbscopy,'choiceform':choiceform,
    'now_user':{'user':request.user,'is_login':request.user.is_authenticated}})


# 发表帖子
@login_required
def topic(request):
    try:
        if request.method == 'POST':
            form = QuestionForm(request.POST,request.FILES or None)
            if form.is_valid():
                topic = form.save(commit=False)
                topic.user = request.user
                topic.save()

    except (KeyError):
        return render(request, 'bbscopy/index.html', {
            'error_message': "页面出错！",
        })

    else:
        return HttpResponseRedirect(reverse('bbscopy:index'))


# 回复帖子
@login_required
def reply(request, bbscopy_id):
    bbscopy = get_object_or_404(Question, pk=bbscopy_id)
    try:
        if request.method == 'POST':
            form = ChoiceForm(request.POST,request.FILES or None)
            # 判断表单是否成功获取
            if form.is_valid():
                # 先不向数据库commit，后面还需绑定问题模型
                reply = form.save(commit=False)
                # 将reply获取到的回复，与问题模型绑定
                reply.question = bbscopy
                # 保险代码，将user给锁定当前登陆的昵称
                reply.user = request.user
                # 保存到数据库
                reply.save()

    except (KeyError):
        return render(request, 'bbscopy/detail.html', {
            'bbscopy': bbscopy,
            'error_message': "页面出错！",
        })

    else:
        return HttpResponseRedirect(reverse('bbscopy:detail', args=(bbscopy.id,)))


class QuestionListView(ListView):
    model = Question
    context_object_name = 'latest_bbscopy_list'
    template_name = 'bbscopy/index.html'

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context['now_user'] = {'user':self.request.user,'is_login':self.request.user.is_authenticated}
        context['questionform'] = QuestionForm()
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('query')
        if query:
            return queryset.filter(
                Q(question_title__icontains=query) | 
                Q(user__username__icontains=query) |
                Q(pub_date__icontains=query)
            ).distinct()
        return queryset


class TopicCreateView(CreateView):
    model = Question
    template_name = 'bbscopy/index.html'
    fields = ('question_title','question_text','picture')

    def form_valid(self,form):
        question = form.save(commit=False)
        question.author = self.request.user
        question.save()
        return HttpResponseRedirect(reverse('bbscopy:index'))


