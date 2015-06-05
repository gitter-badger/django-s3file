# -*- coding:utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.conf.urls import include, patterns, url
from django.views.generic import FormView

from . import forms, views

urlpatterns = patterns(
    '',
    url(r'^s3file/', include('s3file.urls')),
    url(r'^s3/$',
        views.S3MockView.as_view(), name='s3mock'),
    url(r'^upload/$',
        FormView.as_view(form_class=forms.UploadForm, template_name='form.html'), name='upload'),
)
