from django.urls import path

from . import views

app_name = 'courses'

urlpatterns = [
    # ---- Student-facing ----
    path('', views.course_list, name='course_list'),
    path('<int:pk>/', views.course_detail, name='course_detail'),
    path('lesson/<int:pk>/', views.lesson_detail, name='lesson_detail'),
    path('test/<int:pk>/', views.test_take, name='test_take'),
    path('test/<int:pk>/submit/', views.test_submit, name='test_submit'),
    path('result/<int:pk>/', views.test_result, name='test_result'),
    path('assignment/<int:pk>/submit/', views.assignment_submit, name='assignment_submit'),

    # ---- Management dashboard ----
    path('manage/', views.manage_dashboard, name='manage_dashboard'),

    # ---- Courses ----
    path('manage/courses/', views.course_list_manage, name='manage_course_list'),
    path('manage/courses/add/', views.course_create, name='manage_course_create'),
    path('manage/courses/<int:pk>/', views.course_manage, name='manage_course_detail'),
    path('manage/courses/<int:pk>/edit/', views.course_edit, name='manage_course_edit'),
    path('manage/courses/<int:pk>/delete/', views.course_delete, name='manage_course_delete'),

    # ---- Modules ----
    path('manage/courses/<int:course_pk>/modules/add/', views.module_create, name='manage_module_create'),
    path('manage/modules/<int:pk>/edit/', views.module_edit, name='manage_module_edit'),
    path('manage/modules/<int:pk>/delete/', views.module_delete, name='manage_module_delete'),

    # ---- Lessons ----
    path('manage/modules/<int:module_pk>/lessons/add/', views.lesson_create, name='manage_lesson_create'),
    path('manage/lessons/<int:pk>/', views.lesson_manage, name='manage_lesson'),
    path('manage/lessons/<int:pk>/edit/', views.lesson_edit, name='manage_lesson_edit'),
    path('manage/lessons/<int:pk>/delete/', views.lesson_delete, name='manage_lesson_delete'),

    # ---- Videos ----
    path('manage/lessons/<int:lesson_pk>/videos/add/', views.video_create, name='manage_video_create'),
    path('manage/videos/<int:pk>/edit/', views.video_edit, name='manage_video_edit'),
    path('manage/videos/<int:pk>/delete/', views.video_delete, name='manage_video_delete'),

    # ---- Presentations ----
    path('manage/lessons/<int:lesson_pk>/presentations/add/', views.presentation_create, name='manage_presentation_create'),
    path('manage/presentations/<int:pk>/edit/', views.presentation_edit, name='manage_presentation_edit'),
    path('manage/presentations/<int:pk>/delete/', views.presentation_delete, name='manage_presentation_delete'),

    # ---- Materials ----
    path('manage/lessons/<int:lesson_pk>/materials/add/', views.material_create, name='manage_material_create'),
    path('manage/materials/<int:pk>/edit/', views.material_edit, name='manage_material_edit'),
    path('manage/materials/<int:pk>/delete/', views.material_delete, name='manage_material_delete'),

    # ---- Tests ----
    path('manage/lessons/<int:lesson_pk>/tests/add/', views.test_create, name='manage_test_create'),
    path('manage/tests/<int:pk>/edit/', views.test_edit, name='manage_test_edit'),
    path('manage/tests/<int:pk>/delete/', views.test_delete, name='manage_test_delete'),

    # ---- Questions ----
    path('manage/tests/<int:test_pk>/questions/', views.question_manage, name='manage_question'),
    path('manage/tests/<int:test_pk>/questions/add/', views.question_create, name='manage_question_create'),
    path('manage/questions/<int:pk>/edit/', views.question_edit, name='manage_question_edit'),
    path('manage/questions/<int:pk>/delete/', views.question_delete, name='manage_question_delete'),

    # ---- Assignments ----
    path('manage/lessons/<int:lesson_pk>/assignments/add/', views.assignment_create, name='manage_assignment_create'),
    path('manage/assignments/<int:pk>/edit/', views.assignment_edit, name='manage_assignment_edit'),
    path('manage/assignments/<int:pk>/delete/', views.assignment_delete, name='manage_assignment_delete'),

    # ---- Groups (admin) ----
    path('manage/groups/', views.group_list, name='manage_group_list'),
    path('manage/groups/add/', views.group_create, name='manage_group_create'),
    path('manage/groups/<int:pk>/edit/', views.group_edit, name='manage_group_edit'),
    path('manage/groups/<int:pk>/delete/', views.group_delete, name='manage_group_delete'),

    # ---- Grading ----
    path('manage/grading/', views.grading_list, name='manage_grading'),
    path('manage/grading/<int:pk>/', views.grade_submission, name='manage_grade'),
    path('manage/test-results/', views.test_results, name='manage_test_results'),
]
