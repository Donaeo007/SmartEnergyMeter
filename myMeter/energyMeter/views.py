from django.shortcuts import render
import pyrebase # Firebase database
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
    voltage = Sourcedatabase.child('smartMeter').child('voltage').get().val()
    current = Sourcedatabase.child('smartMeter').child('current').get().val()
    power = Sourcedatabase.child('smartMeter').child('power').get().val()
    energy = Sourcedatabase.child('smartMeter').child('energy').get().val()
    cost = Sourcedatabase.child('smartMeter').child('cost').get().val()
    unixtime = Sourcedatabase.child('smartMeter').child('unixtime').get().val()
    Data = {"voltage": voltage, "current": current, "power":power,
            "energy":energy, "cost":cost, "unixtime":unixtime}
    return render(request, "index.html", {"data": Data})


def updateDashboard(request):
    voltage = Sourcedatabase.child('smartMeter').child('voltage').get().val()
    current = Sourcedatabase.child('smartMeter').child('current').get().val()
    power = Sourcedatabase.child('smartMeter').child('power').get().val()
    energy = Sourcedatabase.child('smartMeter').child('energy').get().val()
    cost = Sourcedatabase.child('smartMeter').child('cost').get().val()
    unixtime = Sourcedatabase.child('smartMeter').child('unixtime').get().val()
    updatedData = {"voltage": voltage, "current": current, "power":power,
            "energy":energy, "cost":cost, "unixtime":unixtime}
    return JsonResponse(updatedData)
  


