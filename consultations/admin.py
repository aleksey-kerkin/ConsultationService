from django.contrib import admin

from .models import Consultation, Slot, Specialist, User

admin.site.register(User)
admin.site.register(Specialist)
admin.site.register(Slot)
admin.site.register(Consultation)
