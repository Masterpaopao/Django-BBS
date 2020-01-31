from django.contrib import admin
from .models import Question,Choice

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_title','question_text','user','pub_date')
    list_editable = ('question_title',)
    list_display_links = None
    search_fields = ('question_title','user',)

class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('choice_text','user','question',)
    search_fields = ('choice_text',)

admin.site.register(Question,QuestionAdmin)
admin.site.register(Choice,ChoiceAdmin)