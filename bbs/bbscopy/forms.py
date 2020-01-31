from django import forms
from .models import Question,Choice

class ChoiceForm(forms.ModelForm):
    choice_text = forms.CharField(
        label = "发表评论",
        widget = forms.Textarea(
            attrs={
                'rows':'3',
                'cols':'30',
                'class':'form-control',
                'placeholder':'不超过150字...'
            }
        )
    )
    picture = forms.FileField(
        label = "上传图片(可选)",
        required = False,
        widget = forms.FileInput(
            attrs={
                'class':'form-control',
            }
        )
    )
    class Meta:
        model = Choice
        fields = ['choice_text','picture']

class QuestionForm(forms.ModelForm):
    question_title = forms.CharField(
        label = "帖子标题",
        widget = forms.TextInput(
            attrs={
                'class':'form-control',
                'placeholder':'不超过20字...',
                'minlength':'2',
                'maxlength':'20'
            }
        )
    )
    question_text = forms.CharField(
        label = "帖子内容",
        required = False,
        widget = forms.Textarea(
            attrs={
                'rows':'3',
                'cols':'30',
                'class':'form-control',
                'placeholder':'请尽情畅所欲言...'
            }
        )
    )
    picture = forms.FileField(
        label = "上传图片(可选)",
        required = False,
        widget = forms.FileInput(
            attrs={
                'class':'form-control',
            }
        )
    )
    class Meta:
        model = Question
        fields = ['question_title','question_text','picture']