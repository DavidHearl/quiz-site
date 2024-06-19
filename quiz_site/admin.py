from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Quiz)

# Question Models
admin.site.register(GeneralKnowledge)
admin.site.register(TrueOrFalse)
admin.site.register(Flags)
admin.site.register(Logos)
admin.site.register(Jets)
admin.site.register(Celebrities)
admin.site.register(Movies)
admin.site.register(Locations)
admin.site.register(Questions)
