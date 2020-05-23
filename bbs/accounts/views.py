from django.shortcuts import render,get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from .forms import RegisterForm
from django.contrib.auth.models import User
from .models import UserUpdate
from bbscopy.models import Question
from bbscopy.models import Choice


import hashlib
from django.utils import timezone
from .models import ConfirmString
from django.conf import settings
from django.core.mail import EmailMultiAlternatives

from django.contrib.auth.decorators import login_required


# 个人中心
@login_required
def personal(request):
    
    # 判断是否发生更新信息的行为
    if request.method == 'POST':
        # 先获取到提交的数据集，还有文件
        data = request.POST
        pic  = request.FILES
        # 更改数据
        userupdate = get_object_or_404(UserUpdate,user_id=request.user.id)
        userupdate.sex = data['personal_sex']
        userupdate.country = data['personal_country']
        # 不上传头像，默认不操作
        try:
            userupdate.picture = pic['personal_picture']
        except:
            pass
        # 保存数据    
        userupdate.save()


    now_user_q_list = Question.objects.filter(user_id = request.user.id)
    now_user_c_list = Choice.objects.filter(user_id = request.user.id)

    # 将这个用户的所有回帖id与帖子来源对应起来
    c_to_d_dict = {}
    for c in now_user_c_list:
        # 从原帖对象里面寻找
        c_to_d_dict[c.id] = Question.objects.get(id=c.question_id).question_title

    now_user_d_object = get_object_or_404(UserUpdate, user_id=request.user.id)
    

    context = {
        'now_user':{'user':request.user,'is_login':request.user.is_authenticated},
        'now_user_q':now_user_q_list,
        'now_user_c':now_user_c_list,
        'now_user_d':now_user_d_object,
        'c_to_d_dict':c_to_d_dict,
    }
    
    return render(request,'accounts/personal.html',context)


# 登录
def login_user(request):

    # 发生登录行为的时候，激活这个if代码块
    if request.method == 'POST':
        # 获取POST发送的数据
        username = request.POST['inputName']
        password = request.POST['inputPassword']

        # 判断用户是否在auth_user数据表里 
        user = authenticate(username=username,password=password)
        # 进行登陆操作
        if user:
            # 判断是否经过邮箱验证
            if user.is_superuser:
                login(request,user)
                return HttpResponseRedirect(reverse('bbscopy:index'))
            else:
                error_message = '用户还未邮箱验证！'
                return render(request,'accounts/login.html',{'error_message':error_message})

        else:
            error_message = '用户名或密码错误！'
            return render(request,'accounts/login.html',{'error_message':error_message})

    return render(request,'accounts/login.html')


# 登出
@login_required
def logout_user(request):
    # 自动退出当前正在登陆的帐号
    logout(request)
    return HttpResponseRedirect(reverse('bbscopy:index'))


# 注册
def register_user(request):

    registerform = RegisterForm()

    # 发生注册行为的时候，激活这个if代码块
    if request.method == 'POST':
            form = RegisterForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                username = form.cleaned_data.get('username')
                password1 = form.cleaned_data.get('password1')
                password2 = form.cleaned_data.get('password2')
                email = form.cleaned_data.get('email')
                # 判断密码不一致
                if password1 != password2:
                    error_message = '两次输入的密码不同！'
                    return render(request, 'accounts/register.html', 
                    {'error_message':error_message,'registerform':registerform})
                else:
                     # 判断是否有重名
                    same_name_user = User.objects.filter(username=username)
                    if same_name_user:
                        error_message = '用户名已经存在！'
                        return render(request, 'accounts/register.html', 
                    {'error_message':error_message,'registerform':registerform})
                     # 判断是否有重复邮箱
                    same_email_user = User.objects.filter(email=email)
                    if same_email_user:
                        error_message = '该邮箱已经被注册了！'
                        return render(request, 'accounts/register.html', 
                    {'error_message':error_message,'registerform':registerform})

                # 加密的方式保存密码
                user.set_password(form.cleaned_data['password1'])
                user.save()

                # 外键UserUpdate也应当更新进去用户
                u = UserUpdate.objects.create(user_id=user.id)
                u.save()

                # 发送注册码，激活用户
                code = make_confirm_string(user)
                send_email_for_register(email, code)

                # 发送邮件成功以后，跳转到验证页面
                success_message = '邮箱已发送，请验证邮箱完成注册'
                return render(request,'accounts/prompt.html',{'success_message':success_message})

    return render(request,'accounts/register.html',{'registerform':registerform})


# 验证注册
@login_required
def confirm(request):
    code = request.GET.get('code', None)
    # 先判断url的code是否有效
    try:
        confirm = ConfirmString.objects.get(code=code)
    except:
        error_message = '无效的确认请求!'
        return render(request, 'accounts/confirm.html', {'error_message':error_message})
    
    # confirm一旦被获取到，修改权限，允许登录：
    confirm.user.is_superuser = 1
    confirm.user.save()
    # 用户已经拥有登录权限了,confirm留着没用了
    confirm.delete()
    success_message = '验证邮箱成功！将自动登录'
    return render(request, 'accounts/confirm.html', {'success_message':success_message})


# 跳转
@login_required
def prompt(request):
    return render(request,'accounts/prompt.html')


# 找回密码
def find_password(request):
    if request.method == 'POST':
        username = request.POST['inputName']
        email = request.POST['inputEmail']
        user_object = User.objects.filter(username=username,email=email).first()
        if not user_object:
            error_message = '用户名与邮箱不匹配！'
            return render(request, 'accounts/find_password.html',
            {'error_message':error_message})
        else:
            # 发送编码，找回密码
            code = make_password_string(user_object)
            send_email_for_find(email, code)
            # 发送邮件成功以后，跳转到验证页面
            success_message = '邮箱已发送，请验证邮箱完成校验'
            return render(request,'accounts/prompt.html',{'success_message':success_message})

    return render(request, 'accounts/find_password.html')


# 设置密码
def set_password(request):
    if request.method == 'GET':
        code = request.GET.get('code', None)
        try:
            confirm = ConfirmString.objects.get(code=code)
        except:
            error_message = '无效的确认请求!'
            return render(request, 'accounts/set_password.html',
            {'error_message':error_message, 'success_status':0})
        # 取出要找回密码的用户名字
        user_id = confirm.user_id
        username = User.objects.get(id=user_id).username
        success_message = '请设置你的新密码'
        return render(request, 'accounts/set_password.html',
            {'success_message':success_message, "username":username, 'success_status':0})

    # 提交新密码
    if request.method == 'POST':
        username = request.POST['inputName']
        password1 = request.POST['inputPassword1']
        password2 = request.POST['inputPassword2']
        if password1 != password2:
            error_message = '两次输入的密码不同！'
            return render(request, 'accounts/set_password.html', 
            {'error_message':error_message, "username":username, 'success_status':0})
        else:
            # 设置密码
            user = User.objects.get(username=username)
            user.set_password(password1)
            user.save()
            # 设置成功则删除编码
            confirm = ConfirmString.objects.get(user_id=user.id)
            confirm.delete()
            # 发送设置成功的状态码，跳转到登录界面
            success_message = '设置密码成功，自动跳转中……'
            return render(request, 'accounts/set_password.html', 
                {'success_message':success_message, 'success_status':1})


# 哈希混淆加盐
def hash_code(s, salt='Masterpaopao'):
    h = hashlib.sha256()
    s += salt
    h.update(s.encode())
    return h.hexdigest()


# 确定code注册码
def make_confirm_string(user):
    now = timezone.now()
    code = hash_code(user.username + 'register', str(now))
    ConfirmString.objects.create(code=code, user=user,)
    return code


# 完成发送邮箱的任务-注册用户
def send_email_for_register(email, code):

    subject = '来自黄宇航的毕设项目'

    # 正式消息
    html_content = '''
                    <p>感谢注册<a href="http://{}/accounts/confirm/?code={}" target=blank>www.Masterpaopao.com</a>，\
                    这里是我的毕设项目《基于Python开发的技术交流平台》，邀请你来体验！</p>
                    <p>请点击站点链接完成注册确认！</p>
                    '''.format('127.0.0.1:8000', code,)
    # 备用消息
    text_content = '''感谢注册www.Masterpaopao.com的用户，这里是我的毕设项目《基于Python开发的技术交流平台》，邀请你来体验！\
                    如果你看到这条消息，说明你的邮箱服务器不提供HTML链接功能，请手动复制以下链接访问：
                    http://{}/accounts/confirm/?code={}
                    '''.format('127.0.0.1:8000', code,)

    msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()


# 确定code找回密码
def make_password_string(user):
    now = timezone.now()
    code = hash_code(user.username + 'password', str(now))
    ConfirmString.objects.create(code=code, user_id=user.id,)
    return code


# 完成发送邮箱的任务-找回密码
def send_email_for_find(email, code):

    subject = '来自黄宇航的毕设项目'

    # 正式消息
    html_content = '''
                    <p>找回密码使用这个链接<a href="http://{}/accounts/set_password/?code={}" target=blank>www.Masterpaopao.com</a>，\
                    这里是我的毕设项目《基于Python开发的技术交流平台》，邀请你来体验！</p>
                    <p>请点击站点链接完成找回密码！</p>
                    '''.format('127.0.0.1:8000', code,)
    # 备用消息
    text_content = '''你正在www.Masterpaopao.com上找回密码，这里是我的毕设项目《基于Python开发的技术交流平台》，邀请你来体验！\
                    如果你看到这条消息，说明你的邮箱服务器不提供HTML链接功能，请手动复制以下链接访问：
                    http://{}/accounts/set_password/?code={}
                    '''.format('127.0.0.1:8000', code,)

    msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()