# Copyright (c) 2015-2016 Mikhail Podgurskiy <kmmbvnr@gmail.com>
# All rights reserved.
from __future__ import unicode_literals

from django.contrib.auth import get_permission_codename
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views import generic

from .mixins import MessageUserMixin, ModelViewMixin

from common.sitemodule import module_registry, SITE_TEMPLATE_PACKS

class CreateModelView(MessageUserMixin, ModelViewMixin, generic.CreateView):
    """Thin `generic.CreateView` wrapper plays nice with `ModelViewSet`."""

    template_name_suffix = '_create'

    def has_add_permission(self, request):
        """Object add permission check.

        If view had a `viewset`, the `viewset.has_add_permission` used.
        """
        if self.viewset is not None:
            return self.viewset.has_add_permission(request)

        # default lookup for the django permission
        opts = self.model._meta
        codename = get_permission_codename('add', opts)
        return request.user.has_perm('{}.{}'.format(opts.app_label, codename))

    def get_success_url(self):
        """Redirect back to the detail view if no `success_url` is configured."""
        if self.success_url is None:
            try:
                return self.get_absolute_url(self.object, 'detail')
            except NoReverseMatch:
                pass
            pass
        return super(ModelViewMixin, self).get_success_url()   

    def message_user(self):
        self.success(_('The {name} "{link}" was added successfully.'))

    def get_context_data(self, **kwargs):
        kwargs.setdefault('form_template_pack', SITE_TEMPLATE_PACKS)
        return super().get_context_data(**kwargs)
