from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
from common.sitemodule import SiteModuleMixin

class DashboardConfig(SiteModuleMixin, AppConfig):
    name = 'dashboard'
    verbose_name = _('Home')
    verbose_name_prural = _('Home')

    # Properties for module registration
    label = 'dashboard'
    icon = '<i class="material-icons">home</i>'
    order = 10
    enabled = True

    model_map = { 'dashboard': 'dashboard' }
    # mo: model object
    model_key_map = { 'dashboard': lambda mo: [], }

    @property
    def index_url(self):
        return reverse("index")
    pass


    
