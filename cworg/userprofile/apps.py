from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse

from common.sitemodule import SiteModuleMixin

class UserProfileConfig(SiteModuleMixin, AppConfig):
    ''' User profile config '''
    name = 'userprofile'
    verbose_name = _('User')
    verbose_name_plural = _('Users')

    # Properties for module registration
    label = 'users'
    icon = '<i class="material-icons">person</i>'
    order = 100
    enabled = True
    model_map = { 'userprofile': 'user', 'users': 'user' }

    def index_url(self):
        """Entry url for a site module."""
        return reverse('{}:index'.format(self.label))

    pass
