from django.conf.urls import patterns, include, url
from django.contrib import admin
from quizbook_app import views
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', views.home, name='home'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^login$', views.login_view, name='login'),
    url(r'^logout/$', views.logout_view, name='logout'),
    url(r'^courses/', include('quizbook_app.urls', namespace="courses")),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^get_solution/$', views.get_solution, name='get_solution'),
)
