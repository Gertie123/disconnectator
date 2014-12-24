from django.conf.urls import patterns, url
from django.views.generic import TemplateView

from annotator import views

urlpatterns = patterns('',
    url(r'^thanks/$', views.thanks, name='thanks'),
    url(r'^thanks/(?P<token>\w+)/$', views.thanks, name='thanks'),
    url(r'^ajax/$', views.ajax, name='ajax'),
    url(r'^$', views.dashboard, name='dashboard'),
)
