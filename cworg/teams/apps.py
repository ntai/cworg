from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
from common.sitemodule import SiteModuleMixin

class TeamsConfig(SiteModuleMixin, AppConfig):
    name = 'teams'
    verbose_name = _('Team')
    verbose_name_plural = _('Teams')

    # Properties for module registration
    label = 'teams'
    icon = '<i class="material-icons">group</i>'
    order = 70
    enabled = True
    model_map = {
        'teams': 'team',
        'team': 'team',
        'teammembers': 'member',
        'teammember': 'member',
        'members': 'member',
        'member': 'member',
    }

    # mobj: model object
    model_key_map = { 'team': lambda mobj: [mobj.slug],
                      'member': lambda mobj: [mobj.team.slug, mobj.pk],
                      }

    def index_url(self):
        """Entry url for a site module."""
        return reverse('{}:{}_list'.format(self.label, self.model_map[self.label]))

    pass
