from django.db import models
from django.db.models.signals import pre_save
from django.utils.translation import ugettext_lazy as _
from common.constant import REST_KEYWORDS
from django.utils.text import slugify
from django.utils.safestring import mark_safe


class Location(models.Model):
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=100, default='Unknown location')

    address = models.CharField(max_length=200, blank=True)
    coordinates = models.CharField(max_length=200, blank=True)
    googlemap_url = models.URLField(max_length=200, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    homepage = models.URLField(max_length=200, blank=True)
    description = models.CharField(max_length=1000, blank=True)
    

    class Meta:
        ordering = ("id",)
        pass

    def __str__(self):
        return self.name

    pass

def create_location_slug(instance, new_slug=None):
    slug = slugify(instance.name)
    if new_slug is not None:
        slug = new_slug
        pass
    # If the slug is REST verbs, avoid the conflict.
    exists = slug in REST_KEYWORDS or slug in ['location', 'locations' ]
    if not exists:
        qs = Location.objects.filter(slug=slug).order_by("-id")
        exists = qs.exists()
        pass
    if exists:
        new_slug = "%s-%s" %(slug, qs.first().id)
        return create_location_slug(instance, new_slug=new_slug)
    return slug


def pre_save_location_receiver(sender, instance, *args, **kwargs):
    # 100 attendance is the absolute max
    if not instance.slug:
        instance.slug = create_location_slug(instance)
        pass
    pass

pre_save.connect(pre_save_location_receiver, sender=Location)
