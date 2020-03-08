# Copyright (c) 2015-2016 Mikhail Podgurskiy <kmmbvnr@gmail.com>
# All rights reserved.
#
# Copyright (c) 2020 Naoyuki Tai <ntai11@cleanwinner.com> All rights reserved.
#
from __future__ import unicode_literals

from django.contrib.auth import get_permission_codename
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views import generic

from .mixins import MessageUserMixin, ModelViewMixin

from common.sitemodule import module_registry, SITE_TEMPLATE_PACKS
from cwlog import logger


class UpdateModelView(MessageUserMixin, ModelViewMixin, generic.UpdateView):
    """Thin `generic.UpdateView` wrapper plays nice with `ModelViewSet`."""

    template_name_suffix = '_update'

    def has_object_permission(self, request, obj):
        """Object update permission check.

        If view had a `viewset`, the `viewset.has_update_permission` used.
        """
        if self.viewset is not None:
            return self.viewset.has_update_permission(request, obj)

        # default lookup for the django permission
        opts = self.model._meta
        codename = get_permission_codename('change', opts)
        okay = request.user.has_perm('{}.{}'.format(opts.app_label, codename), obj=obj)
        return okay

    def get_success_url(self):
        """Redirect back to the detail view if no `success_url` is configured."""
        if self.success_url is None:
            return self.get_absolute_url(self.object, 'detail')
        return super(ModelViewMixin, self).get_success_url()

    def message_user(self):
        self.success(_('The {name} "{link}" was updated successfully.'))
        pass

    def get_context_data(self, **kwargs):
        kwargs.setdefault('form_template_pack', SITE_TEMPLATE_PACKS)
        return super().get_context_data(**kwargs)
