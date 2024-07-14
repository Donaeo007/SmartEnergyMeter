# Create your models here.
from django.db import models
from django.utils import timezone


# Create your models here.
# Define choices for the box status


class meterData(models.Model): # stores all new data separately
    cumm_energy =  models.DecimalField(null=False, blank=False, max_digits=10, decimal_places=4) # 67.6876kwh
    power = models.DecimalField(null=False, blank=False, max_digits=10, decimal_places=4)
    current = models.DecimalField(null=False, blank=False, max_digits=10, decimal_places=2)
    voltage = models.DecimalField(null=False, blank=False, max_digits=10, decimal_places=2)
    power_factor = models.DecimalField(null=False, blank=False, max_digits=5, decimal_places=2, default=0)
    unix_time = models.IntegerField(primary_key=True, null=False, blank=False)
    converted_unixtime = models.DateTimeField()
    meter_reset =  models.BooleanField(default=False)
    energy_cost  =  models.DecimalField(null=False, blank=False, max_digits=10, decimal_places=2)
    save_counter = models.IntegerField(null=False, blank=False, default=1)
    
    def __str__(self):
        return str(self.converted_unixtime) + "/" + str(self.cumm_energy) 
    
class configData(models.Model):
    sync_duration = models.IntegerField(null=False, blank = False)
    load_deactivation_duration = models.IntegerField(null=False, blank = False)
    unit_price = models.DecimalField(null=False, blank = False, max_digits=10, decimal_places=2)
    load_threshold = models.DecimalField(null=False, blank = False, max_digits=5, decimal_places=2)
    
    