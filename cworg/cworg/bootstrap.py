from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from meets.models import Meet, Attendee, Assignment
from teams.models import Team, TeamMember
from locations.models import Location
from userprofile.models import UserProfile


cwmembers, created = Group.objects.get_or_create(name='cwmembers')
for model in [Meet, Attendee, Assignment, Team, TeamMember, Location, UserProfile]:
    # Code to add permission to group ???
    cont_type = ContentType.objects.get_for_model(model)

    # Now what - Say I want to add 'Can add project' permission to new_group?
    permission = Permission.objects.create(codename='can_add_project',
                                           name='Can add project',
                                           content_type=cont_type)
    cwmembers.permissions.add(permission)
