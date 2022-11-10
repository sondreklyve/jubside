
"""jubside URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.views.static import serve
from django.views.generic import RedirectView, TemplateView
from . import views

urlpatterns = [
    url(r'^$', views.FrontPageView.as_view(), name='frontpage'),
    url(r'^', include('user.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^album/', include('contentapps.album.urls')),
	url(r'^alumni/$', TemplateView.as_view(template_name='alumni.html')),
    url(r'^arrangement/', include('events.urls')),
    url(r'^favicon\.ico$', RedirectView.as_view(url=settings.STATIC_URL + 'img/favicon.ico', permanent=True)),
    url(r'^markdown/', include('django_markdown.urls')),

    # Del filer (Husk manage.py collectstatic for static filer når DEBUG=False)
    url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    url(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    url(r'^', include('django.contrib.flatpages.urls')),

]

if settings.DEBUG:
    urlpatterns += [
         url(r'^500.html/$', TemplateView.as_view(template_name='500.html')),
         url(r'^404.html/$', TemplateView.as_view(template_name='404.html')),
    ]
