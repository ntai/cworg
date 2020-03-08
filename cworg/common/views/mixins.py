# Copyright (c) 2015-2016 Mikhail Podgurskiy <kmmbvnr@gmail.com>
# All rights reserved.
from __future__ import unicode_literals

from django.contrib import messages
from django.core.exceptions import PermissionDenied, ValidationError, SuspiciousOperation
from django.forms.models import modelform_factory
from django.http import Http404
from django.urls import reverse
from django.utils.encoding import force_text
from django.utils.html import format_html
from django.utils.http import urlquote
from django.utils.translation import ugettext_lazy as _

from cwlog import logger

from material import Span
from ..sitemodule import module_registry, SITE_TEMPLATE_PACKS

def _collect_elements(parent, container=None):
    if container is None:
        container = []

    if hasattr(parent, 'elements'):
        for element in parent.elements:
            _collect_elements(element, container=container)

    if isinstance(parent, Span):
        container.append(parent.field_name)

    return container


class ModelViewMixin(object):
    """Mixin for generic form views to play nice with `ModelViewSet`."""

    viewset = None
    layout = None
    form_widgets = None

    def __init__(self, *args, **kwargs):  # noqa D102
        super(ModelViewMixin, self).__init__(*args, **kwargs)
        if self.form_class is None and self.fields is None:
            if self.layout is not None:
                self.fields = _collect_elements(self.layout)
            else:
                self.fields = '__all__'
                pass
            pass
        pass

    def has_object_permission(self, request, obj):
        """Check object access permission.

        Subclasses should override it
        """
        raise NotImplementedError

    def get_queryset(self):
        """Return the list of items for this view.

        If view have no explicit `self.queryset`, tries too lookup to
        `viewflow.get_queryset`
        """
        if self.queryset is None and self.viewset is not None:
            if hasattr(self.viewset, 'get_queryset'):
                return self.viewset.get_queryset(self.request)
        return super(ModelViewMixin, self).get_queryset()

    def get_object(self):
        """Retrieve an object and check user permissions."""
        queryset = self.get_queryset()
        model = queryset.model
        pk = self.kwargs.get(self.pk_url_kwarg)
        if pk is not None:
            try:
                self.kwargs[self.pk_url_kwarg] = model._meta.pk.to_python(pk)
            except (ValidationError, ValueError):
                raise Http404

        obj = super(ModelViewMixin, self).get_object()
        if not self.has_object_permission(self.request, obj):
            raise PermissionDenied
        return obj


    def get_success_url(self):
        """Redirect back to the list view if no `success_url` is configured."""
        if self.success_url is None:
            return reverse(self.get_named_url('list'))
        return super(ModelViewMixin, self).get_success_url()


    def get_form_class(self):
        if self.form_class is None:
            if self.model is not None:
                model = self.model
            elif hasattr(self, 'object') and self.object is not None:
                model = self.object.__class__
            else:
                model = self.get_queryset().model
            return modelform_factory(model, fields=self.fields, widgets=self.form_widgets)
        return super(ModelViewMixin, self).get_form_class()


    def get_template_names(self):
        """
        List of templates for the view.

        If no `self.template_name` defined, uses::

             [<app_label>/<module_path>_<suffix>.html,
              <app_label>/<module_path>_form.html,
              'common/views/form.html']
        """
        if self.template_name is None:
            opts = self.model._meta
            module = module_registry.get_module(opts.app_label)
            return [
                '{}/{}{}.html'.format(
                    opts.app_label,
                    module.get_model_path(opts.model_name),
                    self.template_name_suffix),
                '{}/{}_form.html'.format(
                    opts.app_label,
                    module.get_model_path(opts.model_name)),
                'common/views/form.html',
            ]

        return [self.template_name]

    def form_valid(self, *args, **kwargs):
        response = super(ModelViewMixin, self).form_valid(*args, **kwargs)
        self.message_user()
        return response

    def message_user(self):
        """Successful notification.

        Subclasses can override it.
        """
        pass

    def get_module(self):
        app_label = self.model._meta.app_label
        module = module_registry.get_module(app_label)
        if module is None:
            raise Exception("Module with app_label {} is not registered.".format(self.model._meta.app_label))
        return module


    def get_named_url(self, url_name):
        '''Just a sugar to call into get_named_url of module.'''
        module = self.get_module()
        return module.get_named_url(self.model._meta.model_name, url_name)


    def get_absolute_url(self, model_object, url_name):
        '''Just a sugar to call into get_absolute_url of module.'''
        module = self.get_module()
        return module.get_absolute_url(model_object, self.model._meta.model_name, url_name)


class MessageUserMixin(object):
    """User notification utilities django.messages framework."""

    def report(self, message, level=messages.INFO, fail_silently=True, **kwargs):
        """Construct message and notify the user."""
        opts = self.model._meta
        # get_named_url comes from model mixin.
        if self.object is not None:
            url = self.get_absolute_url(self.object, 'detail')
        else:
            raise Exception("Your view did not return the instance. Check your save() returns an instance object.")
            pass
        link = format_html('<a href="{}">{}</a>', urlquote(url), force_text(self.object))
        name = force_text(opts.verbose_name)

        options = {
            'link': link,
            'name': name
        }
        options.update(kwargs)
        message = format_html(_(message).format(**options))
        messages.add_message(self.request, messages.SUCCESS, message, fail_silently=True)
        pass

    def success(self, message, fail_silently=True, **kwargs):
        self.report(message, level=messages.SUCCESS, fail_silently=fail_silently, **kwargs)
        pass

    def error(self, message, fail_silently=True, **kwargs):
        self.report(message, level=messages.ERROR, fail_silently=fail_silently, **kwargs)
        pass
    
