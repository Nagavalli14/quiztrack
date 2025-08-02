from django.urls import path
from . import views

urlpatterns = [
    # Home page
    path('', views.home, name='home'),

    # Login routes
    path('student/login/', views.student_login, name='student_login'),
    path('teacher/login/', views.teacher_login, name='teacher_login'),

    # Teacher dashboard: Upload & evaluate quizzes
    path('upload_csv/', views.upload_csv, name='upload_csv'),
    path('evaluate/', views.evaluate_results, name='evaluate_results'),

    # Student dashboard & quiz workflow
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('quiz/<int:test_id>/', views.quiz, name='quiz'),
    path('submit_quiz/', views.submit_quiz, name='submit_quiz'),
    path('quiz-submitted/', views.quiz_submitted, name='quiz_submitted'),

    
    path('delete_test/<int:test_id>/', views.delete_test, name='delete_test'),

    # Logout for both roles
    path('logout/', views.logout_view, name='logout'),
]
