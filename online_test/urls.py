from django.urls import path
from online_test import views

urlpatterns = [
    path('',views.index,name="index"),
    path('dashboard/',views.dashboard,name="dashboard"),
    path('dashboard/add-new-subject/',views.add_new_subject,name="add_new_subject"),
    path('dashboard/subjects/',views.subjects,name="subjects"),
    path('dashboard/subjects/<int:pk>/edit/',views.edit_subject,name="edit_subject"),
    path('dashboard/subjects/<int:pk>/delete/',views.delete_subject,name="delete_subject"),
    path('dashboard/add-new-question/',views.add_new_question,name="add_new_question"),
    path('dashboard/questions/',views.questions,name="questions"),
    path('dashboard/questions/<int:pk>/edit/',views.edit_question,name="edit_question"),
    path('dashboard/questions/<int:pk>/delete/',views.delete_question,name="delete_question"),
    path('dashboard/exam-results/',views.exam_results,name="exam_results"),
    path('dashboard/exam-results/<int:pk>/',views.examinee_exam_result,name="examinee_exam_result"),
    path('dashboard/load-question/<int:pk>/',views.loadQuestionAnswer),
    path('exam/',views.exam,name="exam"),
    path('exam-result/',views.exam_result,name="exam_result"),
    path('login/', views.login_user, name='login'),
    path('signup/',views.signup,name="signup"),
    path('logout/',views.logout_user,name="logout_user"),
    path('get-subscriber/',views.get_subscriber,name="get_subscriber"),
    path('dashboard/send-mail-to-subscriber/',views.send_mail_to_subscriber,name="send_mail_to_subscriber")
]
