from django.shortcuts import render, redirect
import pyrebase # Firebase database
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse  #http: For downloading of csv files, json:for sending data to Ajax Request 
from energyMeter.models import meterData, configData
import pytz # Converting unixtime to standard time
import datetime # Converting unixtime to standard time
import csv  # for downloading csv files
from django.db import IntegrityError

#Machine Learning Libraries
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import numpy as np

import os
from django.conf import settings


# Create your views here.

# super user deatils
# username: meteradmin
#password: smartmeterpassword111

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


#Machine learning Linear regression Model

 # Load the trained model from the file
model_path = os.path.join(settings.BASE_DIR, 'linear_regression_model2.pkl')
lr_model = joblib.load(model_path)


'''
def predictCost(cummEnergyChange, power, powerFactor, voltage, current, timeInterval):
  
    # Load the trained model from the file
    #lr_model = joblib.load('linear_regression_model.pkl')

    # Example new data for prediction
    # Replace this with actual feature values
    predicted_daily_energy =  round(((cummEnergyChange*3600*24)/timeInterval), 3)  
    X_new = np.array([[predicted_daily_energy, power, powerFactor, voltage, current]])  # Example: [cumm energy, Power, PowerFactor, Voltage, Current]

    # Predict the cost
    predicted_cost = lr_model.predict(X_new)

    # Output the result
    # print(f"Predicted Cost: {predicted_cost[0]}")
    return predicted_daily_energy, round(predicted_cost[0], 2)

'''

def predictCost(cummEnergyChange, power, powerFactor, voltage, current, timeInterval):
    # Load the trained model from the file
    model_path = os.path.join(settings.BASE_DIR, 'linear_regression_model2.pkl')
    lr_model = joblib.load(model_path)

    # Calculate the predicted daily energy
    predicted_daily_energy = round(((cummEnergyChange * 3600 * 24) / timeInterval), 3)
    
    # Example new data for prediction (with correct feature names)
    X_new = pd.DataFrame({
        'Cumulative Energy(kWh)': [predicted_daily_energy],  # Replace with actual feature names
        'Power (kW)': [power],
        'Power Factor': [powerFactor],
        'Voltage (v)': [voltage],
        'Current(I)': [current]
    })

    # Predict the cost
    predicted_cost = lr_model.predict(X_new)

    # Output the result
    return predicted_daily_energy, round(predicted_cost[0], 2)


def changeUnixtime(unix_timestamp):
   
    # Convert Unix timestamp to datetime with UTC timezone
    utc_time = datetime.datetime.fromtimestamp(unix_timestamp, tz=pytz.utc)

    # Convert UTC datetime to local time (Africa/Lagos timezone)
    local_time = utc_time.astimezone(pytz.timezone('Africa/Lagos'))

    # Format the date and time string
    new_time = local_time.strftime("%B %d, %Y, %I:%M %p").replace("AM", "a.m.").replace("PM", "p.m.")

    return local_time, new_time

def LoadLineChart(request):
    # Retrieve the latest 5 records and reverse them
    dataList = list(meterData.objects.all().order_by('-unix_time')[:10])
    dataList.reverse()
    
    # Extract labels and data
    
    #labels = [item.converted_unixtime for item in dataList]
    labels = [changeUnixtime(item.unix_time)[1] for item in dataList]
    data = [item.cumm_energy for item in dataList]

    # Prepare data in JSON format
    chart_data = {
        'labels': labels,
        'data': data,
    }

    return JsonResponse(chart_data)

def percentageChange(current, previous):
    
    if previous != 0 or None:
        current = float(current)
        previous = float(previous)
        change = current - previous
        percent_change = round(((change/previous)*100), 2)
    
    else: 
        percent_change = 0.00
    return percent_change

def download_csv(request):
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="meter_data.csv"'
    # DeviceData = boxData.objects.filter(device_id=pk)  # Fetch your data from the database
    # name = "Box_" + DeviceData.device_id + "_data_.csv"
    #response['Content-Disposition'] = 'attachment; filename=' + name + '

    writer = csv.writer(response)
    writer.writerow(['Date & Time', 'Cumulative Energy(kWh)', 'Cost(NGN)',
                      'Power (kW)','Power Factor', 'Voltage (v)', 'Current(I)',
                      'Meter Reset',])  # Add column headers

    DeviceData = meterData.objects.all()  # Fetch your data from the database

    for data in DeviceData:
        writer.writerow([data.converted_unixtime,
                         data.cumm_energy, data.energy_cost, data.power, data.power_factor,
                         data.voltage, data.current,data.meter_reset]) 
    return response


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

def coronahome(request):
    voltage = Sourcedatabase.child('smartMeter').child('meterData').child('voltage').get().val()
    current = Sourcedatabase.child('smartMeter').child('meterData').child('current').get().val()
    power = Sourcedatabase.child('smartMeter').child('meterData').child('power').get().val()
    energy = Sourcedatabase.child('smartMeter').child('meterData').child('energy').get().val()
    cost = Sourcedatabase.child('smartMeter').child('meterData').child('cost').get().val()
    powerfactor = Sourcedatabase.child('smartMeter').child('meterData').child('powerfactor').get().val()
    unixtime = Sourcedatabase.child('smartMeter').child('meterData').child('unixtime').get().val()
    
    convertedTime, new_datetime = changeUnixtime(unixtime)
    
    lastData = meterData.objects.last()
    voltage_change = percentageChange(voltage, lastData.voltage)
    current_change = percentageChange(current, lastData.current)
    power_change = percentageChange(power, lastData.power)
    cost_change = percentageChange(cost, lastData.energy_cost)
    energy_change = percentageChange(energy, lastData.cumm_energy)
    powerfactor_change = percentageChange(powerfactor, lastData.power_factor)
    
    # call ML model
    timeInterval = 2  #Time for reading data from Hardware
    cummEnergyChange = float(energy) - float(lastData.cumm_energy)
    if cummEnergyChange == 0.00:
        cummEnergyChange = power/(3600*1000)
    pred_daily_energy, pred_daily_cost = predictCost(cummEnergyChange, power, powerfactor, voltage, current, timeInterval)
    cumm_daily_energy = pred_daily_energy + float(energy)
    total_daily_cost = round((pred_daily_cost + float(cost)), 2)
    
    Data = {"voltage": voltage, "current": current, "power":round(power, 2),
            "energy":energy, "powerfactor":powerfactor, "cost":round(cost, 2), "unixtime":new_datetime,
            "voltage_change":voltage_change, "current_change":current_change,"power_change":power_change,
            "cost_change":cost_change,"energy_change":energy_change, "powerfactor_change":powerfactor_change,
            "predictedEnergy":cumm_daily_energy, "predictedCost":total_daily_cost}
    
    #dataList = meterData.objects.filter(since=since).order_by('-id')[:5]
    dataList = meterData.objects.all().order_by('-unix_time')[:5]
    dataList = reversed(dataList)
    return render(request, 'corona_index.html', {"data":Data, "dataList":dataList})


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
    
    lastData = meterData.objects.last()
    voltage_change = percentageChange(voltage, lastData.voltage)
    current_change = percentageChange(current, lastData.current)
    power_change = percentageChange(power, lastData.power)
    cost_change = percentageChange(cost, lastData.energy_cost)
    energy_change = percentageChange(energy, lastData.cumm_energy)
    powerfactor_change = percentageChange(powerfactor, lastData.power_factor)
    
    
    
    if voltage != 0: 
        voltageGuage = round(((voltage*100)/250), 2)
    else:
        voltageGuage = 0
    
    if current != 0: 
        currentGuage = round(((current*100)/2), 2)
    else:
        currentGuage = 0    
    
    if power != 0: 
        powerGuage = round(((power*100)/200), 2)
    else:
        powerGuage = 0
        
    # call ML model
    timeInterval = 2000  #Time for reading data from Hardware
    cummEnergyChange = float(energy) - float(lastData.cumm_energy)
    if cummEnergyChange == 0.00:
        cummEnergyChange = float(power/(3600*1000))
        timeInterval = 1
    pred_daily_energy, pred_daily_cost = predictCost(cummEnergyChange, power, powerfactor, voltage, current, timeInterval)
    cumm_daily_energy = pred_daily_energy + float(energy)
    total_daily_cost = round((pred_daily_cost + float(cost)), 2)
    updatedData = {"voltage": voltage, "current": current, "power":round(power, 2),
            "energy":energy, "powerfactor":powerfactor,"cost":round(cost, 2),
            "unixtime":new_datetime,"resetMeter":reset_meter,"voltage_change":voltage_change,
            "current_change":current_change,"power_change":power_change,"energy_change":energy_change,
            "predictedEnergy":cumm_daily_energy, "predictedCost":total_daily_cost,
            "cost_change":cost_change,
            "voltageGuageFill":voltageGuage,
            "currentGuageFill":currentGuage,
            "powerGuageFill":powerGuage,"powerfactor_change":powerfactor_change}
    counter += 1
    
    if counter%10 == 0:
        try:
            new_meter_data = meterData.objects.create(save_counter=counter,energy_cost=round(cost,2), meter_reset=reset_meter,
                                                      converted_unixtime=convertedTime, unix_time=unixtime,
                                                      power_factor=powerfactor, voltage=voltage, current=current,
                                                      power=round(power, 2), cumm_energy=energy)
        except IntegrityError:
            latest_data.save_counter = counter
            latest_data.save()  
    else:
        latest_data.save_counter = counter
        latest_data.save()      
    
    return JsonResponse(updatedData)

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
