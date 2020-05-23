from django import forms
from django.contrib.auth.models import User

class RegisterForm(forms.ModelForm):
    username = forms.CharField(
        label='用户名',
        widget = forms.TextInput(
            attrs={
                'minlength':'3',
                'maxlength':'8',
                'class':'form-control',
                'placeholder':'请设置用户名...'
            }
        )
    )
    password1 = forms.CharField(
        label='密码',
        widget = forms.PasswordInput(
            attrs={
                'minlength':'6',
                'maxlength':'18',
                'class':'form-control',
                'placeholder':'请设置密码...'
            }
        )
    )
    password2 = forms.CharField(
        label='再次输入密码',
        widget = forms.PasswordInput(
            attrs={
                'minlength':'6',
                'maxlength':'18',
                'class':'form-control',
                'placeholder':'请确保您的两次输入密码一致...'
            }
        )
    )
    email = forms.CharField(
        label = '邮箱',
        widget = forms.EmailInput(
            attrs={
                'class':'form-control',
                'placeholder':'请设置你的邮箱...'
            }
        )
    )
    class Meta:
        model = User
        fields = ('username','password1','password2','email')

    # 全局钩子，判断两次输入是否相等
    def clean(self):
        if self.cleaned_data["password1"] == self.cleaned_data["password2"]:
            return self.cleaned_data