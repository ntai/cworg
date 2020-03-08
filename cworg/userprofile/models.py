from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

#from meets.models import Meet, Attendee
#from teams.models import Team, TeamMember


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(blank=True, null=True)
    sms = models.CharField(max_length=20, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=200, blank=True)
    fullname = models.CharField(max_length=100, blank=True)

    # teams = models.ManyToManyField(Team)
    # meets = models.ManyToManyField(Meet)
    # attendees = models.ManyToManyField(Attendee)

    class Meta:
        ordering = ("id",)
        pass

    def __str__(self):
        return self.fullname if self.fullname else str(self.user)

    @property
    def display_name(self):
        if self.fullname:
            return self.fullname
        if self.user.first_name or self.user.last_name:
            return "{} {}".format(self.user.first_name, self.user.last_name)
        return self.user.username

    pass

@receiver(post_save, sender=User)
def upsert_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    instance.userprofile.save()
    pass

def get_user_display_name(self):
    userprof = UserProfile.objects.get(user=self)
    if userprof:
        return userprof.display_name
    if self.first_name or self.last_name:
        return "{} {}".format(self.first_name, self.last_name)
    return self.username

User.add_to_class("__str__", get_user_display_name)
