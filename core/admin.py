from django.contrib import admin
from .models import Crop, Compound, EnvironmentData

admin.site.register(Crop)
admin.site.register(Compound)
admin.site.register(EnvironmentData)
