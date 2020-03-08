from django.contrib import admin

# Register your models here.
from .models import Meet, Attendee, Assignment

admin.site.register(Meet)
admin.site.register(Attendee)
admin.site.register(Assignment)
