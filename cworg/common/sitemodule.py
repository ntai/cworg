import warnings
from importlib import import_module

from django.apps import AppConfig, apps
from django.template import Template, TemplateDoesNotExist
from django.template.loader import get_template, select_template
from django.urls import reverse, NoReverseMatch
from django.utils.module_loading import module_has_submodule

from django.urls import URLResolver
from django.urls.resolvers import RegexPattern

from django.utils.decorators import classproperty

from cwlog import logger

SITE_TEMPLATE_PACKS="cwomaterial"


class SiteModuleURLResolver(URLResolver):
    def __init__(self, regex, urlconf_name, default_kwargs=None, app_name=None, namespace=None, module=None):  # noqa D102
        self._module = module
        if app_name is None and namespace is not None:
            app_name = namespace
            pass
        pattern = RegexPattern(regex, is_endpoint=False)
        super(ModuleURLResolver, self).__init__(
            pattern,
            urlconf_name,
            default_kwargs,
            app_name=app_name,
            namespace=namespace,
        )
        pass

    def resolve(self, *args, **kwargs):  # noqa D102
        result = super(ModuleURLResolver, self).resolve(*args, **kwargs)

        if result and not getattr(self._module, 'installed', True):
            raise Resolver404({'message': 'Module not installed'})

        result.url_name = ModuleMatchName(result.url_name)
        result.url_name.module = self._module

        return result
    pass



class SiteModuleRegistry(object):
    """SiteModule registry."""

    def __init__(self):
        self._registry = {}
        self._modules = {}
        pass

    def modules(self):
        """List of site modules in the frontend according to it's order."""
        return sorted([module for module in self._registry.values()],
                      key=lambda scomp: (scomp.order, scomp.label))

    def enabled_modules(self):
        """List of enabled sitecomps.

        A frontend sitecomp itself determines if it enabled or not.
        If the sitecomp instance have no `enabled` attribute, the
        sitecomp considered enabled.
        """
        return [scomp for scomp in self.modules()
                if getattr(scomp, 'enabled', True)]

    def available_modules(self, user):
        """List of site modules permitted for the user."""
        return [sitecomp for sitecomp in self.enabled_modules() if sitecomp.has_perm(user)]

    def get_module(self, label):
        """Get site module by label."""
        return self._registry.get(label, self._modules.get(label, None))

    def register(self, module):
        """Register a site module.

        Can be called on the package level.
        """
        tagvalues = "\n".join(["%s: %s" % (attr, str(getattr(module, attr))) for attr in dir(module) if attr in ['create', 'menu', 'name', 'label'] ])
        # tagvalues = "\n".join(["%s" % (attr) for attr in dir(module) if attr not in ['urls'] ])
        logger.debug("module {} registered.\ndir : {}".format(module.label, tagvalues ))
        self._registry[module.label] = module
        self._modules[module.name] = module
        pass

    @property
    def urls(self):
        """Collected list of all site modules url.

        Even unenabled site modules urls returned here. The site module url
        config have the responsibility to check the site module enabled
        state.
        """
        patterns = []
        for sitecomp in self.modules():
            patterns.append(sitecomp.urls)
            pass
        return patterns

    pass

module_registry = SiteModuleRegistry()


class SiteModuleMixin(object):
    """Extension for the django AppConfig. Makes django app pluggable at runtime.

    The application have to have <app_module>/urls.py file, with
    a single no-parametrized url with name='index', ex::

        urlpatterns = [
            url('^$', generic.TemplateView.as_view(template_name="sales/index.html"), name="index"),
        ]

    All AppConfigs urls will be included into material.frontend.urls automatically under /<app_label>/ prefix
    The AppConfig.label, used for the urls namespace.

    The menu.html sample::

        <ul>
            <li><a href="{% url 'sales:index' %}">Dashboard</a></li>
            <li><a href="{% url 'sales:customers' %}">Customers</a></li>
            {% if perms.sales.can_add_lead %}<li><a href="{% url 'sales:leads' %}">Leads</a></li>{% endif %}
        </ul>

    In all application templates, the current application config
    instance would be available as `current_sitecomp` template variable

    :keyword order: The relative sitecomp order priority. SiteModules in the
                    site menu would be listed according its priorities.

    :keyword icon: The sitecomp icon.

    :keyword enabled: Site is enabled. Default is True

    :keyword model_map: canonicalize the model name.
                        (ex. userprofile -> user, userprofiles -> user)
                        Usefull when 

    :keyword model_key_map: Produce the keys for accesing the model object.
      The map is dict, and the key is the canonicalized model name, and the value is a function that returns an array. 
      The value function's array contains the keys for the URL access. 
      For example, if the URL is /meets/<meet_slug>/attendees/<attendee_id>, the function returns
      [ model_object.meet.slug, model_object.id ] so the function would look like
      lambda model_object: [model_object.meet.slug, model_object.id]
      
    Example::

        class Sales(SiteModuleMixin, AppConfig):
            name = 'sales'
            icon = '<i class="material-icons">call</i>'

    """

    order = 10
    icon = '<i class="material-icons">receipt</i>'
    model_map = None
    model_key_map = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        module_registry.register(self)
        pass

    @classproperty
    def enabled(self):
        return object.__getattribute__(self, 'enabled')

    @classproperty
    def label(self):
        return object.__getattribute__(self, 'name')

    @classproperty
    def order(self):
        return object.__getattribute__(self, 'order')

    @property
    def verbose_name(self):
        """SiteModule name."""
        return self.label.title()

    def description(self):
        """SiteModule description.

        By default taken from the site module docstring.
        """
        return (self.__doc__ or "").strip()

    def has_perm(self, user):
        """Check is user have permission to access to the site module."""
        return True

    def get_urls(self):  # noqa D102
        if module_has_submodule(self.module, 'urls'):
            urls_module_name = '%s.%s' % (self.name, 'urls')
            urls_module = import_module(urls_module_name)
            if hasattr(urls_module, 'urlpatterns'):
                return urls_module.urlpatterns

        warnings.warn('SiteModule {} have not urls.py submodule or `urlpatterns` in it'.format(self.label))
        return []

    @property
    def urls(self):
        """SiteModule url config.

        By default it would be loaded from '<app>/urls.py'
        """
        base_url = r'^{}/'.format(self.label)
        return SiteModuleURLResolver(base_url, self.get_urls(), module=self, app_name=self.label, namespace=self.label)


    def index_url(self):
        """Entry url for a site module."""
        try:
            return reverse('{}:index'.format(self.label))
        except NoReverseMatch as exc:
            msg = "NoReverseMatch: The module {} does not have the named URL '{}:index'. Add the name='index' in urls.py.".format(self.name, self.label)
            raise Exception(msg)
        pass


    def menu(self):
        """Load site module menu template.

        Template should be located in `<app_label>/menu.html`

        If no template exists, no exception raised.

        Intended to use with {% include %} template tag::

            {% include module.menu %}
        """
        try:
            return get_template('{}/menu.html'.format(self.label))
        except TemplateDoesNotExist:
            return Template('')

    def base_template(self):
        """Base template for a module.

        If  <app_label>/base_module.html exists it would be used.
        The default is 'material/frontend/base_module.html'

        Intended to use in modules generic templates. Ex::

            {% extends current_module.base_template %}
        """
        return select_template(['{}/base_module.html'.format(self.label),
                                'site/base/base.html'
        ])


    def get_model_path(self, model_name):
        '''returns the module's URL path from the top.
        :model_name: The name of model
        '''
        if self.model_map is None:
            self.model_map = {model_name: self.label}
            pass
        return self.model_map.get(model_name, model_name)


    def get_named_url(self, model_name, url_name):
        model_path = self.get_model_path(model_name)
        return '{}:{}_{}'.format(self.label, model_path, url_name)


    def get_absolute_url(self, model_object, model_name, url_name):
        '''get the absolute URL for the model object.'''
        model_path = self.get_model_path(model_name)
        try: 
            return reverse(self.get_named_url(model_name, url_name),
                           args=self.get_model_key(model_object, model_path))
        except NoReverseMatch as exc:
            logger.debug('No reverse for url {} with keys {}'.format(self.get_named_url(model_name, url_name), self.get_model_key(model_object, model_path)))
            raise exc
        pass


    def get_model_key(self, model_object, model_path):
        ''' get the key for reverse() to work for the model path '''
        if self.model_key_map:
            model_key = self.model_key_map.get(model_path)
            if model_key:
                if callable(model_key):
                    return model_key(model_object)
                return model_key
            pass
        return [model_object.pk]

    pass


def context_processor(request):
    """Add current site module and site module list to the template context."""
    if not hasattr(request, 'user'):
        raise ValueError('site module context processor requires "django.contrib.auth.context_processors.auth"'
                         'to be in TEMPLATE_CONTEXT_PROCESSORS in your settings file.')
    module = None

    if request.resolver_match:
        module = module_registry.get_module(request.resolver_match.app_name)
        if module is None:
            logger.info('You need to add SiteModuleMixin to AppConfig instance of "{}"'.format(request.resolver_match.app_name))
            attrs = ", ".join( "{}={}".format(attr, getattr( request.resolver_match, attr, "None")) for attr in [ 'url_name', 'app_name', 'namespace', 'route', 'viewName'])
            logger.debug("request.resolver_match ==> {}".format(attrs))
            pass
        logger.debug("module ==> {}".format("None" if module is None else module.name))
        pass
    else:
        logger.debug("request.resolver_match is None")
        pass

    modules = module_registry.available_modules(request.user)

    logger.debug("n-modules {}: {} in {}".format(len(modules), module.name if module is not None else "NONE", ",".join([module.name for module in modules])))

    return {
        'modules': modules,
        'current_module': module,
    }
