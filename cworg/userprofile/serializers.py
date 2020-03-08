
from django.contrib.auth.models import User, Group

from django.contrib.auth.models import User, Group
from .models import Meet, Attendee, Assignment
from locations.models import Location
from teams.models import Team, TeamMember

from rest_framework import serializers
from .models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):

    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.get(user_id))
    image =serializers.ImageField(blank=True, null=True)
    sms = serializers.CharField(max_length=20, blank=True)
    phone = serializers.CharField(max_length=20, blank=True)
    address = serializers.CharField(max_length=200, blank=True)

    teams = serializers.ManyToManyField(Team)
    meets = serializers.ManyToManyField(Meet)
    attendees = serializers.ManyToManyField(Attendee)

    class Meta:
        model = UserProfile
        fields  = ['user', 'image', 'sms', 'phone', 'address']
        pass

    
    def create(self, validated_data):
        """
        Create and return a new `Attendee` instance, given the validated data.
        """
        return UserProfile.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Attendee` instance, given the validated data.
        """
        instance.image = validated_data.get('image', instance.player)
        instance.sms = validated_data.get('sms', instance.sms)

        instance.phone = validated_data.get('phone', instance.phone)
        instance.address = validated_data.get('address', instance.address)

        # instance.teams = validated_data.get('teams', instance.teams)
        # instance.meets = validated_data.get('meets', instance.meets)
        # instance.attendees = validated_data.get('attendees', instance.attendees)

        instance.save()
        return instance

    
