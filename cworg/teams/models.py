from django.db import models
from django.db.models.signals import pre_save
from django.contrib.auth.models import Group, User
from django.utils.text import slugify
from django.utils.safestring import mark_safe
from common.constant import REST_KEYWORDS

from django.utils import timezone

class Team(models.Model):
    #
    slug = models.SlugField(unique=True)

    name = models.CharField(max_length=100, blank=True)

    # Password for joining the team
    join_password = models.CharField(max_length=40)

    # Team creation date
    date_created = timezone.datetime.now()

    # This is Django's group, may or may not be linked
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, blank=True, null=True)

    description = models.CharField(max_length=200, null=True, blank=True, default='')

    owner = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    pass


def create_team_slug(instance, new_slug=None):
    slug = slugify(instance.name)
    if new_slug is not None:
        slug = new_slug
        pass
    # If the slug is REST verbs, avoid the conflict.
    exists = slug in REST_KEYWORDS
    if not exists:
        qs = Team.objects.filter(slug=slug).order_by("-id")
        exists = qs.exists()
        pass
    if exists:
        new_slug = "%s-%s" %(slug, qs.first().id)
        return create_team_slug(instance, new_slug=new_slug)
    return slug


def pre_save_team_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_team_slug(instance)
        pass
    pass

pre_save.connect(pre_save_team_receiver, sender=Team)


class TeamMember(models.Model):
    member = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    rating = models.IntegerField(default=100)
    played = models.IntegerField(default=0)
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    
    def __str__(self):
        return str(self.member)

    class Meta:
        unique_together = ('member', 'team',)

    pass

