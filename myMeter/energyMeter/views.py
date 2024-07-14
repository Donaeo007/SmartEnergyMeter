from django.shortcuts import render, redirect
import pyrebase # Firebase database
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse  #http: For downloading of csv files, json:for sending data to Ajax Request 
from energyMeter.models import meterData, configData
import pytz # Converting unixtime to standard time
import datetime # Converting unixtime to standard time
import csv  # for downloading csv files
from django.db import IntegrityError
# Create your views here.


firebaseConfig = {
  "apiKey": "AIzaSyBK3M1HN0ZaOiJFzvxAWnpWnmCtdNmPzFs",
  "authDomain": "smartmeter-65108.firebaseapp.com",
  "databaseURL": "https://smartmeter-65108-default-rtdb.firebaseio.com",
  "projectId": "smartmeter-65108",
  "storageBucket": "smartmeter-65108.appspot.com",
  "messagingSenderId": "189216592800",
  "appId": "1:189216592800:web:34999bb818cda37002cac5",
  "measurementId": "G-XW2GFDCB98"
}


# Initialize Firebase
firebase = pyrebase.initialize_app(firebaseConfig)
authentiction = firebase.auth()
Sourcedatabase = firebase.database()


'''

def LoadLineChart(request):  # Currently in use to load kine chart
    # Generate sample data for the chart (replace with your actual data retrieval logic)
    label = ['time1', 'time 2', 'time 3', 'time4', 'time5',
             'time6','time7','time8','time9','time10','time11','time12']
    data = [randint(0, 30) for _ in range(len(label))]  # Random data for demo

    # Prepare data in JSON format
    chart_data = {
        'label': label,
        'data': data,
    }

    return JsonResponse(chart_data)
'''


def download_csv(request, pk):
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="meter_data.csv"'
    # DeviceData = boxData.objects.filter(device_id=pk)  # Fetch your data from the database
    # name = "Box_" + DeviceData.device_id + "_data_.csv"
    #response['Content-Disposition'] = 'attachment; filename=' + name + '

    writer = csv.writer(response)
    writer.writerow(['Date & Time', 'Cumulative Energy(kWh)', "Cost(NGN)"
                      'Power (kW)', 'Voltage (v)', 'Current(I)',
                      'Meter Reset',])  # Add column headers

    DeviceData = meterData.objects.all()  # Fetch your data from the database

    for data in DeviceData:
        writer.writerow([data.converted_unixtime,
                         data.cumm_energy, data.cost, data.power, data.voltage,
                         data.current,data.meter_reset]) 
    return response



def changeUnixtime(unix_timestamp):
   
    # Convert Unix timestamp to datetime with UTC timezone
    utc_time = datetime.datetime.fromtimestamp(unix_timestamp, tz=pytz.utc)

    # Convert UTC datetime to local time (Africa/Lagos timezone)
    local_time = utc_time.astimezone(pytz.timezone('Africa/Lagos'))

    # Format the date and time string
    new_time = local_time.strftime("%B %d, %Y, %I:%M %p").replace("AM", "a.m.").replace("PM", "p.m.")

    return local_time, new_time


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
    
    convertedTime, new_datetime = changeUnixtime(unixtime)
      
    Data = {"voltage": voltage, "current": current, "power":power,
            "energy":energy, "powerfactor":powerfactor, "cost":cost, "unixtime":new_datetime}
    return render(request, "index.html", {"data": Data})


def updateDashboard(request):
    latest_data = meterData.objects.order_by('save_counter').last()
    if latest_data is None:
        counter = 1     
    else:
        counter = latest_data.save_counter

    voltage = Sourcedatabase.child('smartMeter').child('meterData').child('voltage').get().val()
    current = Sourcedatabase.child('smartMeter').child('meterData').child('current').get().val()
    power = Sourcedatabase.child('smartMeter').child('meterData').child('power').get().val()
    energy = Sourcedatabase.child('smartMeter').child('meterData').child('energy').get().val()
    powerfactor = Sourcedatabase.child('smartMeter').child('meterData').child('powerfactor').get().val()
    cost = Sourcedatabase.child('smartMeter').child('meterData').child('cost').get().val()
    unixtime = Sourcedatabase.child('smartMeter').child('meterData').child('unixtime').get().val()
    reset_meter = Sourcedatabase.child('smartMeter').child('meterData').child('resetMeter').get().val()
 
    convertedTime, new_datetime = changeUnixtime(unixtime)
    updatedData = {"voltage": voltage, "current": current, "power":power,
            "energy":energy, "powerfactor":powerfactor,"cost":cost, "unixtime":new_datetime,"resetMeter":reset_meter}
    counter += 1
    
    
    if counter%10 == 0:
        try:
            new_meter_data = meterData.objects.create(save_counter=counter,energy_cost=cost, meter_reset=reset_meter,
                                                      converted_unixtime=convertedTime, unix_time=unixtime,
                                                      power_factor=powerfactor, voltage=voltage, current=current,
                                                      power=power, cumm_energy=energy)
        except IntegrityError:
            latest_data.save_counter = counter
            latest_data.save()  
    else:
        latest_data.save_counter = counter
        latest_data.save()      
    
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

