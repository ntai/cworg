from django.db import models
from django.db.models.signals import pre_save
from django.contrib.auth.models import Group, User

from django.utils.translation import ugettext_lazy as _
from django.utils.text import slugify
from django.utils.safestring import mark_safe

from locations.models import Location
from teams.models import Team, TeamMember
from common.constant import REST_KEYWORDS
from cworg.constant import MAX_ATTENDEES
from userprofile.models import UserProfile
from django.utils import timezone
import datetime

from markdown_deux import markdown
import uuid


# One 
class Meet(models.Model):
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=100, default='Unnamed Event')
    team = models.ForeignKey(Team, related_name="team", on_delete=models.SET_NULL, null=True, blank=True)
    group = models.ForeignKey(Group, related_name="group", on_delete=models.SET_NULL, null=True, blank=True)
    starttime = models.DateTimeField('Meet date/time')
    duration = models.DurationField('Duration', default=90)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    min_attendees = models.PositiveIntegerField(default=1)
    max_attendees = models.PositiveIntegerField(default=1)
    comments = models.CharField(max_length=200, null=True, blank=True, default='')

    def __str__(self):
        return self.name

    # def attendee_set(self):
    #     return Attendee.objects.filter(meet=self.id).filter(player__isnull=False)

    def attendee_set(self):
        return Attendee.objects.filter(meet=self.id)

    def get_comments_markdown(self):
        return mark_safe(markdown(self.comments))

    def save(self, *args, **kwargs):
        # Check how the current values differ from ._loaded_values. For example,
        # prevent changing the creator_id of the model. (This example doesn't
        # support cases where 'creator_id' is deferred).

        if self.manager is None:
            self.manager = self.team.owner
            pass
        super().save(*args, **kwargs)

        Attendee.allocate_slots(self, self.min_attendees)
        pass

    class Meta:
        ordering = ("id",)
        verbose_name = _("Meet")
        verbose_name_plural = _("Meets")
        pass

    pass


def create_meet_slug(instance, new_slug=None):
    if new_slug is not None:
        slug = new_slug
    else:
        datestring = str(instance.starttime)
        slug = slugify("{}-{}".format(instance.name, datestring))
        pass
    # If the slug is REST verbs, avoid the conflict.
    exists = slug in REST_KEYWORDS or slug in ['attendance', 'attendees', 'attendee', 'meets', 'meet']
    if not exists:
        qs = Meet.objects.filter(slug=slug).order_by("-id")
        exists = qs.exists()
        pass
    if exists:
        new_slug = "%s-%s" %(slug, qs.first().id)
        return create_meet_slug(instance, new_slug=new_slug)
    return slug


def pre_save_meet_receiver(sender, instance, *args, **kwargs):
    # 100 attendance is the absolute max
    instance.min_attendees = min(MAX_ATTENDEES, instance.min_attendees)
    instance.max_attendees = max(instance.max_attendees, instance.min_attendees)

    if not instance.slug:
        instance.slug = create_meet_slug(instance)
        pass
    pass

pre_save.connect(pre_save_meet_receiver, sender=Meet)


# Attendee

class Attendee(models.Model):
    class Attendance(models.TextChoices):
        NO         = '--', _('Unassinged')
        ASSIGNED   = 'AS', _('Assigned')
        NEED_A_SUB = 'NS', _('Need a sub')
        CONFIRMED  = 'OK', _('Confirmed')
        pass

    meet = models.ForeignKey(Meet, on_delete=models.CASCADE, related_name="meet")
    player = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name="attendee")

    attendance = models.CharField(max_length=2,
                                  choices=Attendance.choices,
                                  default=Attendance.NO)
    substitute = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name="substitute")

    token = models.CharField(max_length=32, unique=True, default=uuid.uuid4().hex)
    token_expiration = models.DateTimeField('Token expiration time', default=timezone.datetime.now()+datetime.timedelta(1, 0))

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['meet', 'player'], name='Unique player in the lineup')
        ]

        verbose_name = _("Attendee")
        verbose_name_plural = _("Attendees")
        ordering = ("id",)
        pass

    def is_confirmed(self):
        return self.attendance in { Attendance.CONFIRMED, Attendance.SUBBED}

    def __str__(self):
        if self.player:
            return str(self.player)
        return "Unassigned"


    def allocate_slots(meet, min_slots):
        current_slots = Attendee.objects.filter(meet=meet).count()
        
        if current_slots < min_slots:
            attendees = []
            for i in range(min_slots - current_slots):
                attendees.append(Attendee(meet=meet, player=None, attendance=Attendee.Attendance.NO, substitute=None))
                pass
            Attendee.objects.bulk_create(attendees)
            pass
        pass

    def get_substitute_display(self):
        if self.substitute:
            return self.substitute
        return ""

    pass


def pre_save_attendee_receiver(sender, instance, *args, **kwargs):
    # If the attendace is unassigned but got a player assigned, update the state to assigned.
    if instance.attendance == Attendee.Attendance.NO and instance.player != None:
        instance.attendance = Attendee.Attendance.ASSIGNED
        pass

    if not instance.token:
        instance.token = uuid.uuid4().hex
        pass
    pass

pre_save.connect(pre_save_attendee_receiver, sender=Attendee)

#
# Assignment
#
class Assignment(models.Model):
    meet = models.ForeignKey(Meet, on_delete=models.CASCADE, null=True, blank=True)
    assignee = models.ForeignKey(Attendee, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.CharField(max_length=200)
    starttime = models.DateTimeField('Assignment date/time')
    pass

