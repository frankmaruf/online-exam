from django.urls import path
from online_test import views

urlpatterns = [
    path('',views.index,name="index"),
    path('dashboard/',views.dashboard,name="dashboard"),
    path('add-new-subject/',views.add_new_subject,name="add_new_subject"),
    path('subjects/',views.subjects,name="subjects"),
    path('subjects/<int:pk>/edit/',views.edit_subject,name="edit_subject"),
    path('subjects/<int:pk>/delete/',views.delete_subject,name="delete_subject"),
    path('add-new-question/',views.add_new_question,name="add_new_question"),
    path('questions/',views.questions,name="questions"),
    path('questions/<int:pk>/edit/',views.edit_question,name="edit_question"),
    path('questions/<int:pk>/delete/',views.delete_question,name="delete_question"),
    path('load-question/<int:pk>/',views.loadQuestionAnswer),
    path('exam/',views.exam,name="exam"),
    path('exam-result/',views.exam_result,name="exam_result"),
    path('exam-results/',views.exam_results,name="exam_results"),
    path('login/', views.login_user, name='login'),
    path('signup/',views.signup,name="signup"),
    path('logout/',views.logout_user,name="logout_user"),
    path('get-subscriber/',views.get_subscriber,name="get_subscriber"),
    path('send-mail-to-subscriber/',views.send_mail_to_subscriber,name="send_mail_to_subscriber")
]
