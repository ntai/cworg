from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse

from common.sitemodule import SiteModuleMixin


class LocationsConfig(SiteModuleMixin, AppConfig):
    name = 'locations'
    verbose_name = _('Location')
    verbose_name_plural = _('Locations')

    # Properties for module registration
    label = 'locations'
    icon = '<i class="material-icons">place</i>'
    order = 80
    enabled = True
    model_map = { 'locations': 'location', 'location': 'location' }
    # mo: model object
    model_key_map = { 'location': lambda mo: [mo.slug], }

    def index_url(self):
        """Entry url for a site module."""
        return reverse('{}:{}_list'.format(self.label, self.model_map[self.label]))

    pass
