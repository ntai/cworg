# Copyright (c) 2015-2016 Mikhail Podgurskiy <kmmbvnr@gmail.com>
# All rights reserved.
from __future__ import unicode_literals

from django.contrib.auth import get_permission_codename
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import models
from django.http import Http404
from django.urls import reverse, NoReverseMatch
from django.views import generic
from django.utils.translation import ugettext_lazy as _

from common.sitemodule import module_registry, SITE_TEMPLATE_PACKS

from cwlog import logger

class DetailModelView(generic.DetailView):
    """Thin wrapper for `generic.DetailView`."""

    viewset = None

    def get_object_data(self):
        """List of object fields to display.

        Choice fields values are expanded to readable choice label.
        """
        fields = getattr(self, 'fields', None)

        for field in self.object._meta.fields:
            if isinstance(field, models.AutoField) or isinstance(field, models.SlugField):
                continue
            elif field.auto_created:
                continue
            elif fields is not None and field.name not in fields:
                continue
            else:
                choice_display_attr = "get_{}_display".format(field.name)
                pass

            if hasattr(self.object, choice_display_attr):
                value = getattr(self.object, choice_display_attr)()
            else:
                value = getattr(self.object, field.name)
                pass

            if value is not None:
                yield (field.verbose_name.title(), value)
                pass
            pass
        pass

    
    def has_view_permission(self, request, obj):
        """Object view permission check.

        If view had a `viewset`, the `viewset.has_view_permission` used.
        """
        if self.viewset is not None:
            return self.viewset.has_view_permission(request, obj)

        # default lookup for the django permission
        opts = self.model._meta
        codename = get_permission_codename('view', opts)
        view_perm = '{}.{}'.format(opts.app_label, codename)
        if request.user.has_perm(view_perm):
            return True
        elif request.user.has_perm(view_perm, obj=obj):
            return True
        return self.has_update_permission(request, obj=obj)

    def has_update_permission(self, request, obj):
        """Object chane permission check.

        If view had a `viewset`, the `viewset.has_update_permission` used.

        If true, view will show `Update` link to the Update view.
        """
        if self.viewset is not None:
            return self.viewset.has_update_permission(request, obj)

        # default lookup for the django permission
        opts = self.model._meta
        codename = get_permission_codename('change', opts)
        update_perm = '{}.{}'.format(opts.app_label, codename)

        logger.debug('DetailModelView.has_update_permission: {}'.format(update_perm))

        if request.user.has_perm(update_perm):
            return True
        return request.user.has_perm(update_perm, obj=obj)

    def has_delete_permission(self, request, obj):
        """Object delete permission check.

        If true, view will show `Delete` link to the Delete view.
        """
        if self.viewset is not None:
            return self.viewset.has_delete_permission(request, obj)

        # default lookup for the django permission
        opts = self.model._meta
        codename = get_permission_codename('delete', opts)
        delete_perm = '{}.{}'.format(opts.app_label, codename)
        if request.user.has_perm(delete_perm):
            return True
        return request.user.has_perm(delete_perm, obj=obj)

    def get_object(self):
        """Retrieve the object.

        Check object view permission at the same time.
        """
        queryset = self.get_queryset()
        model = queryset.model
        pk = self.kwargs.get(self.pk_url_kwarg)
        if pk is not None:
            try:
                self.kwargs[self.pk_url_kwarg] = model._meta.pk.to_python(pk)
            except (ValidationError, ValueError):
                raise Http404

            pass

        obj = super(DetailModelView, self).get_object()
        if not self.has_view_permission(self.request, obj):
            raise PermissionDenied
        return obj

    def get_context_data(self, **kwargs):
        """Additional context data for detail view.

        :keyword object_data: List of fields and values of the object
        :keyword update_url: Link to the update view
        :keyword delete_url: Link to the delete view
        """
        kwargs.setdefault('form_template_pack', SITE_TEMPLATE_PACKS)

        opts = self.model._meta
        kwargs['object_data'] = self.get_object_data()

        if self.has_update_permission(self.request, self.object):
            try:
                kwargs['update_url'] = self.get_absolute_url(self.object, 'update')
                logger.debug("detail.get_context_data: update_url {}".format(kwargs['update_url']))
                pass
            except NoReverseMatch:
                logger.debug("update_url {} does not exist.".format(self.get_named_url('update')) )
                pass
            pass
        else:
            logger.debug("detail.get_context_data: no update_url due to perm.")
            pass


        if self.has_delete_permission(self.request, self.object):
            try:
                kwargs['delete_url'] = self.get_absolute_url(self.object, 'delete')
                logger.debug("detail.get_context_data: delete_url {}".format(kwargs['update_url']))
                pass
            except NoReverseMatch:
                logger.debug("delete_url {} does not exist.".format(self.get_named_url('delete')) )
                pass
            pass

        return super(DetailModelView, self).get_context_data(**kwargs)

    def get_template_names(self):
        """
        List of templates for the view.

        If no `self.template_name` defined, returns::

             [<app_label>/<model_label>_detail.html
              'common/views/detail.html']
        """
        if self.template_name is None:
            opts = self.model._meta
            module = self.get_module()
            return [
                '{}/{}{}.html'.format(
                    opts.app_label,
                    module.get_model_path(opts.model_name),
                    self.template_name_suffix),
                'site/model_detail.html',
            ]

        return [self.template_name]

    def get_module(self):
        '''get module from the model'''
        opts = self.model._meta
        module = module_registry.get_module(opts.app_label)
        if module is None:
            raise Exception("Module with app_label {} is not registered.".format(opts.app_label))
        return module

    def get_named_url(self, url_name):
        '''Just a sugar to call into get_named_url of module.'''
        opts = self.model._meta
        module = self.get_module()
        return module.get_named_url(opts.model_name, url_name)
    
    def get_absolute_url(self, model_object, url_name):
        '''Just a sugar to call into get_absolute_url of module.'''
        module = self.get_module()
        return module.get_absolute_url(model_object, self.model._meta.model_name, url_name)

    def dispatch(self, request, *args, **kwargs):
        kwargs.setdefault('form_template_pack', SITE_TEMPLATE_PACKS)
        return super().dispatch(request, *args, **kwargs)

    pass
