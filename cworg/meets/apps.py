from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse

from common.sitemodule import SiteModuleMixin


class MeetsConfig(SiteModuleMixin, AppConfig):
    '''Meets config'''
    # Module property
    # name should match with the app_name in urls.py
    name = 'meets'
    verbose_name = _('Meet')
    verbose_name_plural = _('Meets')

    # Properties for module registration
    label = 'meets'
    icon = '<i class="material-icons">events</i>'
    order = 30
    enabled = True
    model_map = { 'meets': 'meet', 'attendees': 'attendee' }
    # mo: model object
    model_key_map = { 'meet': lambda mo: [mo.slug],
                      'attendee': lambda mo: [mo.meet.slug, mo.pk],
                      }

    def has_perm(self, user):
        return True

    def index_url(self):
        """Entry url for a site module."""
        return reverse('{}:{}_list'.format(self.label, self.model_map[self.label]))

    pass
