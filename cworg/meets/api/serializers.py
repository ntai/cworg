# Models
from django.contrib.auth.models import User, Group
from meets.models import Meet, Attendee, Assignment
from locations.models import Location
from teams.models import Team, TeamMember

from rest_framework import serializers

from userprofile.api.serializers import UserDetailSerializer


class MeetSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)

    name = serializers.CharField(max_length=100)
    team = serializers.PrimaryKeyRelatedField(many=False, allow_null=True, queryset=Team.objects.all())
    group = serializers.CharField(max_length=100)

    starttime = serializers.DateTimeField()
    duration = serializers.DurationField(min_value=0)
    location = serializers.PrimaryKeyRelatedField(many=False, allow_null=True, queryset=Location.objects.all())
    manager = serializers.PrimaryKeyRelatedField(many=False, allow_null=True, queryset=User.objects.all())
    min_attendees = serializers.IntegerField(min_value=1)
    max_attendees = serializers.IntegerField(min_value=1)

    attendees = serializers.PrimaryKeyRelatedField(many=True, queryset=Attendee.objects.all())

    def create(self, validated_data):
        """
        Create and return a new `Meet` instance, given the validated data.
        """
        return Meet.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Meet` instance, given the validated data.
        """
        instance.name = validated_data.get('name', instance.name)
        instance.team = validated_data.get('team', instance.team)
        instance.group = validated_data.get('group', instance.group)

        instance.starttime = validated_data.get('starttime', instance.starttime)
        instance.duration = validated_data.get('duration', instance.duration)

        instance.location = validated_data.get('location', instance.location)
        instance.manager = validated_data.get('manager', instance.manager)
        instance.min_attendees = validated_data.get('min_attendees', instance.min_attendees)
        instance.max_attendees = validated_data.get('max_attendees', instance.max_attendees)

        instance.save()
        return instance

    pass


class AttendeeSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    meet = serializers.CharField(max_length=100)
    player = serializers.CharField(max_length=100)
    attendance = serializers.CharField(max_length=2)
    substitute = serializers.CharField(required=False, allow_blank=True, max_length=100)
    token = serializers.CharField(max_length=32)

    def create(self, validated_data):
        """
        Create and return a new `Attendee` instance, given the validated data.
        """
        return Attendee.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Attendee` instance, given the validated data.
        """
        instance.meet = validated_data.get('meet', instance.meet)
        instance.player = validated_data.get('player', instance.player)
        instance.attendance = validated_data.get('attendance', instance.attendance)
        instance.substitute = validated_data.get('substitute', instance.substitute)
        instance.token = validated_data.get('token', instance.token)
        instance.token_expiration = validated_data.get('token_expiration', instance.token_expiration)
        return instance
    pass


class MeetCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meet
        fields = [
            #'id',
            'name',
            'team',
            'starttime',
            'location',
            'manager'
        ]


meet_detail_url = serializers.HyperlinkedIdentityField(
        view_name='meets-api:detail',
        lookup_field='pk'
        )


class MeetDetailSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(read_only=True)

    name = serializers.CharField(max_length=100)
    team = serializers.PrimaryKeyRelatedField(many=False, allow_null=True, queryset=Team.objects.all())
    group = serializers.PrimaryKeyRelatedField(many=False, allow_null=True, queryset=Group.objects.all())

    starttime = serializers.DateTimeField()
    duration = serializers.DurationField(min_value=0)
    location = serializers.PrimaryKeyRelatedField(many=False, allow_null=True, queryset=Location.objects.all())
    manager = serializers.PrimaryKeyRelatedField(many=False, allow_null=True, queryset=User.objects.all())
    min_attendees = serializers.IntegerField(min_value=1)
    max_attendees = serializers.IntegerField(min_value=1)

    comments = serializers.CharField(max_length=200)

    def create(self, validated_data):
        """
        Create and return a new `Meet` instance, given the validated data.
        """
        return Meet.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Meet` instance, given the validated data.
        """
        instance.slug = validated_data.get('slug', instance.name)
        instance.name = validated_data.get('name', instance.name)
        instance.team = validated_data.get('team', instance.team)
        instance.group = validated_data.get('group', instance.group)

        instance.starttime = validated_data.get('starttime', instance.starttime)
        instance.duration = validated_data.get('duration', instance.duration)

        instance.location = validated_data.get('location', instance.location)
        instance.manager = validated_data.get('manager', instance.manager)
        instance.min_attendees = validated_data.get('min_attendees', instance.min_attendees)
        instance.max_attendees = validated_data.get('max_attendees', instance.max_attendees)

        instance.save()
        return instance


    class Meta:
        model = Meet
        fields = [
            'id',
            'slug',
            'name',
            'location',
            'team',
            'group',
            'starttime',
            'duration',
            'manager',
            'min_attendees',
            'max_attendees',
            'comments',
        ]

    def get_html(self, obj):
        return obj.get_markdown()

    def get_comments(self, obj):
        c_qs = Comment.objects.filter_by_instance(obj)
        comments = CommentSerializer(c_qs, many=True).data
        return comments

    pass


class MeetListSerializer(serializers.ModelSerializer):
    #manager = UserDetailSerializer(read_only=True)

    class Meta:
        model = Meet
        fields = [
            'slug',
            'name',
            'team',
            'starttime',
            'manager',
            'comments',
        ]
        pass
    pass


from rest_framework.validators import UniqueValidator

class AttendanceActionSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    attendance = serializers.CharField(max_length=2)
    token = serializers.CharField(max_length=32)

    def create(self, validated_data):
        """
        No creation
        """
        return None

    def update(self, instance, validated_data):
        """
        Update and return an existing `Attendee` instance, given the validated data.
        """
        instance.attendance = validated_data.get('attendance', instance.attendance)
        instance.token = validated_data.get('token', instance.token)
        return instance
    pass

