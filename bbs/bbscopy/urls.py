from django.urls import path
from . import views

app_name = "bbscopy"
urlpatterns = [
    # path('', views.QuestionListView.as_view(), name='index'),
    path('', views.index, name='index'),
    # path('topic/', views.TopicCreateView.as_view(), name='topic'),
    path('topic/', views.topic, name='topic'),
    path('reply/<int:bbscopy_id>/', views.reply, name='reply'),
    path('detail/<int:bbscopy_id>/', views.detail, name='detail'),
]
