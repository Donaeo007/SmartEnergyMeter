from django.contrib import admin
from energyMeter.models import meterData, configData

# Register your models here.
admin.site.register(meterData)
admin.site.register(configData)