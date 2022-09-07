import django
from django.urls import path, include

from lms import settings
from . import views
from django.contrib.auth import views as auth_views

from django.contrib.auth import views as auth_views


urlpatterns = [

    # Shared URLs
    path('', views.home, name='home'),
    path('lsign/', views.LearnerSignUpView.as_view(), name='lsign'),
    path('login_form/', views.login_form, name='login_form'),
    path('login/', views.loginView, name='login'),
    path('logout/', views.logoutView, name='logout'),
    path('prof/', views.ProfView.as_view(), name='profcourses'),
    path('ent/', views.ENT.as_view(), name='entcourses'),
    path('demo/', views.Demo.as_view(), name='demo'),

    path('access', views.AccessList.as_view(), name='access'),
    path("password_reset", views.password_reset_request, name="password_reset"),
    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name="password_reset_confirm.html"),
         name='password_reset_confirm'),
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'),
         name='password_reset_complete'),
    # Admin URLs
    path('dashboard/', views.dashboard, name='dashboard'),
    path('course/', views.course, name='course'),
    path('post_course/', views.post_course, name='post_course'),
    path('aluser/', views.ListUserView.as_view(), name='aluser'),
    path('aduser/<int:pk>', views.ADeleteuser.as_view(), name='aduser'),
    path('acreate_profile/', views.acreate_profile, name='acreate_profile'),
    path('profile/', views.createprofile, name='profile'),

    path('auser_profile/', views.auser_profile, name='auser_profile'),
    path('acourse/', views.ListCourseView.as_view(), name='list_course'),
    path('dcourse/<int:pk>', views.ADeleteCourse.as_view(), name='dcourse'),
    path('acourse/<int:pk>', views.course_detail.as_view(), name='course_detail'),
    path('user/<int:pk>', views.user_detail.as_view(), name='user_detail'),

    path('update/<int:pk>', views.update_course, name='update_object'),
    path('update/updaterecord/<int:pk>', views.updaterecord, name='updaterecord'),
    path('add/<int:pk>', views.addcourse, name='addcourse'),
    path('updatet/<int:pk>', views.update_tutorial, name='update_tutorial'),
    path('updatet/updatetutor/<int:pk>', views.updatetutor, name='updatetutor'),
    path('addfile/<int:pk>', views.add_file, name='addfile'),
    path('addfile/addf/<int:pk>', views.addfile, name='addf'),
    path('tutorial/<int:pk>', views.tutorial, name='tutorial'),
    path('itutorials/<int:pk>/', views.ITutorialDetail.as_view(), name="itutorial-detail"),
    path('post/', views.publish_tutorial, name='publish_tutorial'),
    path('lesson/<int:pk>', views.module, name='itut'),
    path('usercourse/<int:pk>', views.usercourse, name='usercourse'),
    path('courseu/<int:pk>', views.courseu, name='courseu'),
    path('dusercourse/<int:pk>', views.dusercourse, name='dusercourse'),
    path('coursed/<int:pk>', views.coursed, name='coursed'),

    path('module/', views.module, name='module'),
    path('postmodule/', views.publish_module, name='publish-module'),

    # Instructor URLs
    path('quiz_add/<int:pk>', views.QuizCreateView.as_view(), name='quiz_add'),
    path('question_add/<int:pk>', views.question_add, name='question_add'),
    path('quiz/<int:quiz_pk>/<int:question_pk>/', views.question_change, name='question_change'),
    path('llist_quiz/', views.QuizListView.as_view(), name='quiz_change_list'),
    path('quiz/<int:quiz_pk>/question/<int:question_pk>/delete/', views.QuestionDeleteView.as_view(),
         name='question_delete'),
    path('quiz/<int:pk>/results/', views.QuizResultsView.as_view(), name='quiz_results'),
    path('quiz/<int:pk>/delete/', views.QuizDeleteView.as_view(), name='quiz_delete'),
    path('quizupdate/<int:pk>/', views.QuizUpdateView.as_view(), name='quiz_change'),
    path('rating/<int:pk>', views.Rating.as_view(), name='rating'),

    # Learner URl's
    path('learner/', views.ShopView.as_view(), name='learner'),
    path('lcreate_profile/', views.lcreate_profile, name='lcreate_profile'),
    path('taken/<int:pk>', views.TakenQuizListView.as_view(), name='taken_quiz_list'),
    path('quiz/<int:pk>/', views.take_quiz, name='take_quiz'),
    path('shop/', views.ShopView.as_view(), name='shop'),
    path('courses/<int:pk>', views.scourse.as_view(), name='course'),
    path('buy/<int:pk>', views.buycourse, name='buy'),
    path('mycourses/', views.showmycourses, name='mycourses'),
    path('lessons/<int:pk>', views.Lesson.as_view(), name='lessons'),
    path('complete/<int:pk>', views.paymentComplete, name="complete"),
    path('test', views.model_form_view, name='test')

]
