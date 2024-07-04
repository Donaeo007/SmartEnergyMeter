from django.shortcuts import render, redirect
import pyrebase # Firebase database
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse  #http: For downloading of csv files, json:for sending data to Ajax Request 
# Create your views here.


firebaseConfig = {
  "apiKey": "AIzaSyD-c45EtVmZ4PYWdP6uce7HsmqLcIdoUhc",
  "authDomain": "ecowise-48198.firebaseapp.com",
  "databaseURL": "https://ecowise-48198-default-rtdb.firebaseio.com",
  "projectId": "ecowise-48198",
  "storageBucket": "ecowise-48198.appspot.com",
  "messagingSenderId": "513968660014",
  "appId": "1:513968660014:web:7ea6028e88ee874aee49bf",
  "measurementId": "G-TMN6ZQX0DX"
}

# Initialize Firebase
firebase = pyrebase.initialize_app(firebaseConfig)
authentiction = firebase.auth()
Sourcedatabase = firebase.database()


def homepage(request):
#    voltage = 225.22
#    current = 5.4
#    power =  1020
    voltage = Sourcedatabase.child('smartMeter').child('meterData').child('voltage').get().val()
    current = Sourcedatabase.child('smartMeter').child('meterData').child('current').get().val()
    power = Sourcedatabase.child('smartMeter').child('meterData').child('power').get().val()
    energy = Sourcedatabase.child('smartMeter').child('meterData').child('energy').get().val()
    cost = Sourcedatabase.child('smartMeter').child('meterData').child('cost').get().val()
    powerfactor = Sourcedatabase.child('smartMeter').child('meterData').child('powerfactor').get().val()
    unixtime = Sourcedatabase.child('smartMeter').child('meterData').child('unixtime').get().val()
    Data = {"voltage": voltage, "current": current, "power":power,
            "energy":energy, "powerfactor":powerfactor, "cost":cost, "unixtime":unixtime}
    return render(request, "index.html", {"data": Data})


def updateDashboard(request):
    voltage = Sourcedatabase.child('smartMeter').child('meterData').child('voltage').get().val()
    current = Sourcedatabase.child('smartMeter').child('meterData').child('current').get().val()
    power = Sourcedatabase.child('smartMeter').child('meterData').child('power').get().val()
    energy = Sourcedatabase.child('smartMeter').child('meterData').child('energy').get().val()
    powerfactor = Sourcedatabase.child('smartMeter').child('meterData').child('powerfactor').get().val()
    cost = Sourcedatabase.child('smartMeter').child('meterData').child('cost').get().val()
    unixtime = Sourcedatabase.child('smartMeter').child('meterData').child('unixtime').get().val()
    updatedData = {"voltage": voltage, "current": current, "power":power,
            "energy":energy, "powerfactor":powerfactor,"cost":cost, "unixtime":unixtime}
    return JsonResponse(updatedData)
  

# Sourcedatabase.child('smartMeter').child(meterData).update({'resetMeter': DeviceData.switch_reset})



@csrf_exempt
def update_parameters(request):
    cost = Sourcedatabase.child('smartMeter').child('configData').child('unitPrice').get().val()
    load_treshold = Sourcedatabase.child('smartMeter').child('configData').child('loadThreshold').get().val()
    load_deactivation_duration = Sourcedatabase.child('smartMeter').child('configData').child('loadDeactivateDuration').get().val()
    sync_duration = Sourcedatabase.child('smartMeter').child('configData').child('syncDuration').get().val()
    reset_meter = Sourcedatabase.child('smartMeter').child('meterData').child('resetMeter').get().val()
    
    if request.method == 'POST':
        field = request.POST.get('submit')
        value = request.POST.get(field)
        
        # Here you can update your model or configuration with the new value
        # Example:
        if field == 'unit_cost':
             #update_unit_cost(value)
             cost = value
             Sourcedatabase.child('smartMeter').child('configData').update({'unitPrice': float(cost)})
        elif field == 'load_threshold':
                load_treshold = value
                Sourcedatabase.child('smartMeter').child('configData').update({'loadThreshold': float(load_treshold)})
             #update_load_threshold(value)
        elif field == 'load_duration':
                load_deactivation_duration = value
                Sourcedatabase.child('smartMeter').child('configData').update({'loadDeactivateDuration': int(load_deactivation_duration)})
             #update_load_threshold(value)
        elif field == "sync_duration":
                sync_duration = value
                Sourcedatabase.child('smartMeter').child('configData').update({'syncDuration': int(sync_duration)})
             #update_load_threshold(value)
        elif field == 'reset_meter':
                if value == "on":
                    reset_meter = True
                else: 
                    reset_meter = False
                Sourcedatabase.child('smartMeter').child('meterData').update({'resetMeter': reset_meter})
             #update_load_threshold(value)
        # etc.
        new_context = {
        'unit_cost': cost,
        'load_threshold': load_treshold,
        'load_deactivation_duration': load_deactivation_duration,
        'synctimer_duration': sync_duration,
        'reset_meter': False,
        }
        return render(request, 'parameters.html', new_context)

    # Render the template with the current values
    context = {
        'unit_cost': cost,
        'load_threshold': load_treshold,
        'load_deactivation_duration': load_deactivation_duration,
        'synctimer_duration': sync_duration,
        'reset_meter': False,
       }
    return render(request, 'parameters.html', context)

