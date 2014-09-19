from django.conf.urls import patterns, include, url
from django.contrib import admin
from quizbook import views
from quizbook_app import views as quizbook_app_views
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', quizbook_app_views.home, name='home'),
    url(r'^signup/$', quizbook_app_views.signup, name='signup'),
    url(r'^login$', quizbook_app_views.login_view, name='login'),
    url(r'^logout/$', quizbook_app_views.logout_view, name='logout'),
    url(r'^courses/', include('quizbook_app.urls', namespace="courses")),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^get_solution/$', quizbook_app_views.get_solution, name='get_solution'),
    url(r'^about/$', views.get_about, name='about'),
    url(r'^add_solution/*$', quizbook_app_views.add_solution_ajax),

)
