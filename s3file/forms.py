# -*- coding:utf-8 -*-
from __future__ import unicode_literals

import logging
import os

from django.conf import settings
from django.core.files import File
from django.core.files.storage import default_storage
from django.core.urlresolvers import reverse_lazy
from django.forms.widgets import ClearableFileInput
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe

logger = logging.getLogger('s3file')


class S3FileInput(ClearableFileInput):
    """
    FileInput that uses JavaScript to directly upload to Amazon S3.
    """
    needs_multipart_form = False
    signing_url = reverse_lazy('s3file-sign')
    template = (
        '<div class="s3file" data-policy-url="{policy_url}">'
        '  <a class="file-link" target="_blank" href="{file_url}">{file_name}</a>'
        '  <a class="file-remove" href="#remove">Remove</a>'
        '  <input class="file-url" type="hidden" value="{file_url}"'
        ' id="{element_id}" name="{name}" />'
        '  <input class="file-input" type="file" />'
        '  <div class="progress progress-striped active">'
        '    <div class="bar"></div>'
        '  </div>'
        '</div>'
    )

    def render(self, name, value, attrs=None):
        final_attrs = self.build_attrs(attrs)
        element_id = final_attrs.get('id')

        if isinstance(value, File):
            file_url = default_storage.url(value.name)
            file_name = os.path.basename(value.name)
        else:
            file_url = ''
            file_name = ''

        if file_url:
            input_value = 'initial'
        else:
            input_value = ''

        output = self.template.format(
            policy_url=self.signing_url,
            file_url=file_url,
            file_name=file_name,
            element_id=element_id or '',
            name=name,
            value=input_value,
            remove=force_text(self.clear_checkbox_label)
        )

        return mark_safe(output)

    def value_from_datadict(self, data, files, name):
        filename = data.get(name)
        if not filename:
            return None
        elif filename == 'initial':
            return False
        try:
            f = default_storage.open(filename)
            return f
        except IOError:
            logger.exception('File "%s" could not be found.', filename)
            return False

    class Media:
        js = (
            's3file/js/s3file.js',

        )
        css = {
            'all': (
                's3file/css/s3file.css',
            )
        }


def AutoFileInput(*args, **kwargs):
    """
    A factory method that returns ether an instance of S3FileInput
    of ClearableFileInput depending on whether or not the S3 Key is
    set in django.config.settings.
    :
        Settings example:
        AWS_SECRET_ACCESS_KEY='asdf'
    :
    :return: S3FileInput, django.forms.ClearableFileInput
    """
    if hasattr(settings, 'AWS_SECRET_ACCESS_KEY') \
            and settings.AWS_SECRET_ACCESS_KEY:
        return S3FileInput(*args, **kwargs)
    else:
        return ClearableFileInput(*args, **kwargs)
