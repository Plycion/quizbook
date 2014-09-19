from django.conf.urls import patterns, url
from quizbook_app import views
from django.contrib import admin
admin.autodiscover()
from quizbook_app import views as quizbook_app_views

urlpatterns = patterns(
    '',
    url(r'^$', views.index, name='index'),
    url(r'^print_courses/$', views.text_courses, name='text_courses'),
    url(r'^latex_courses/$', views.latex_courses, name='latex_courses'),
    url(r'^new_course/$', views.new_course_page, name='new_course_page'),
    url(r'^new_course/process$', views.new_course_process, name='new_course_process'),

    url(r'^(?P<course_id>\d+)/$', views.detail, name='detail'),
    url(r'^(?P<course_id>\d+)/practice/$', views.practice_question, name='practise'),
    # url(r'^(?P<course_id>\d+)/random/$', views.random_quiz, name='random_quiz'),
    url(r'^(?P<course_id>\d+)/enroll/$', views.enroll_user_in_course, name='enroll'),
    url(r'^(?P<course_id>\d+)/drop/$', views.drop_user_from_course, name='drop'),
    url(r'^(?P<course_id>\d+)/delete/$', views.delete_course, name='delete_course'),
    url(r'^(?P<course_id>\d+)/new_quiz/$', views.new_quiz_page, name='new_quiz_page'),
    url(r'^(?P<course_id>\d+)/new_quiz/process/$', views.new_quiz_process, name='new_quiz_process'),

    url(r'^(?P<course_id>\d+)/quiz/$', views.quiz, name='quiz'),
    url(r'^\d+/quiz(?P<quiz_id>\d+)/answer/$', views.practice_answer, name='answer'),

    url(r'^(?P<course_id>\d+)/(?P<quiz_id>\d+)/$', views.quiz_page, name='quiz_page'),
    url(r'^(?P<course_id>\d+)/(?P<quiz_id>\d+)/delete/$', views.delete_quiz, name='delete_quiz'),
    url(r'^(?P<course_id>\d+)/(?P<quiz_id>\d+)/update/$', views.update_quiz, name='update_quiz'),
    url(r'^(?P<course_id>\d+)/(?P<quiz_id>\d+)/edit/$', views.edit_quiz_page, name='edit_quiz'),
    url(r'^(?P<course_id>\d+)/(?P<quiz_id>\d+)/edit/process/$', views.edit_quiz_process, name='edit_quiz_process'),
    url(r'^(?P<course_id>\d+)/(?P<quiz_id>\d+)/add_solution/$', views.add_solution, name='add_solution'),
    url(r'^(?P<course_id>\d+)/(?P<quiz_id>\d+)/add_solution/process/$', views.process_add_solution, name='process_add_solution'),
    url(r'^(?P<course_id>\d+)/(?P<quiz_id>\d+)/upvote/$', views.upvote_solution, name='upvote_solution'),
    url(r'^(?P<course_id>\d+)/(?P<quiz_id>\d+)/delete_solution/$', views.delete_solution, name='delete_solution'),
)
