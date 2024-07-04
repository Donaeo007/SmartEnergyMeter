#include <SPI.h>  
#include <Wire.h>
#include <EEPROM.h>
#include <ESP8266WiFi.h>
#include <time.h>
#include <LiquidCrystal_I2C.h>
#include <PZEM004Tv30.h>
#include <SoftwareSerial.h>
#include <ArduinoJson.h>
#include "FirebaseESP8266.h" 
#include "addons/TokenHelper.h"
#include "addons/RTDBHelper.h"


LiquidCrystal_I2C lcd(0x27, 16, 2);  // set the LCD address to 0x27 for a 16 chars and 2 line display

int8_t TIME_ZONE = 1; //NYC(USA): -5 UTC

//INTERNET CONNECTIVITY DATA
#define WIFI_SSID "HBDESKTOP"
#define WIFI_PASSWORD "habeebpc111"

//DB CONFIGURATION DATA
//Comment if user login is not required
#define API_KEY "AIzaSyBK3M1HN0ZaOiJFzvxAWnpWnmCtdNmPzFs"

/* 3. Define the RTDB URL */
#define DATABASE_URL "https://smartmeter-65108-default-rtdb.firebaseio.com/" 
#define DATABASE_SECRET "YddvtPTzh2eeg5CFILSrQIzyVNPmxP0UIJ6DSwqN"

/* 4. Define the user Email and password that alreadey registerd or added in your project */
//Note: Not required for anonymous user
#define USER_EMAIL "mymeter@gmail.com"
#define USER_PASSWORD "mymeter111"



//PZEM-004T CONFIGURATION DATA
#if !defined(PZEM_RX_PIN) && !defined(PZEM_TX_PIN)
#define PZEM_RX_PIN D4 // D4 is wemos RX pin to be connected to TXpin on PZEM (yellow)
#define PZEM_TX_PIN D6  //D6 is wemos TX pin to be connected to RXpin of PZEM)(white)
#endif

SoftwareSerial pzemSWSerial(PZEM_RX_PIN, PZEM_TX_PIN);
PZEM004Tv30 pzem(pzemSWSerial);

bool resetMeter = false;


//User ID on DB
String base_path = "/UsersData/";  //This is  a constant path to users login details on Firebase DB  
String userID = "Meter01"; //Energy Meter 001- Unique DB address for user 
String uidPath = "/userID/";  //user ID path
String dataPath = "/smartMeter/meterData/";  //Egg data path
String configDataPath = "/smartMeter/configData/";
String resetMeterPath = "resetMeter/";
String loadThresholdPath = "setLoad/";
String keyPath[8] ={"voltage/", "current/","power/","energy/", "powerfactor/", "cost/","unixtime/","resetMeter/"};
String jsonKeys[8] ={"voltage", "current","power","energy", "powerfactor","cost", "unixtime","resetMeter"};
float dataValue_float[7] ={0.00,0.00,0.00,0.00,0.00, 0.00};
int dataValue_int[2] = {0};
bool dataValue_bool[2] = {false};
bool holdResetData[2] = {resetMeter};
String resetDataPath[2] = {resetMeterPath};
String configKeyPath[4]={"loadThreshold/", "unitPrice/", "syncDuration/", "loadDeactivateDuration/" };
float configDataValue_float[3] = {0.00, 0.00};
int configDataValue_int[3] = {0, 0};
int DBdata = 9;
//FirebaseJson json;

//Define an array to hold Firebase data, authentication and configuration objects
FirebaseData fbdo;
FirebaseJson json;  //to hold son to be sent to dB
FirebaseJsonArray arr; //to hold array to be sent to DB
FirebaseAuth auth;
FirebaseConfig config;



//Parameters to be measured
String cost_msg = "Cost(N):"; // 8
String energy_msg = "E(Kwh):"; // 7
String factor_msg = "F:"; //4  --- 0.52
String power_msg = "P:      W"; // 5
String current_msg = "I:     A"; // start 7: 4 + 4 = 8
String voltage_msg = "V:   V"; // 2+3+1+1 = 7
float current = 0.00;
int voltage = 0.00; // set a default voltage
float power = 0.00;
float energy = 0.0000;
float powerfactor = 0.0000;
float unit_price = 0.00;
float cost =0.00;
float load_threshold =  0.2;  // 1 A 

bool deactivate_load = false;

//Configure actuators
//int redLed = A0;
int buzzer = D7; 
int relay =  D5;



//TIMER CONFIGURATION DATA
unsigned long currentDBUpdate;
unsigned long lastDBUpdate=0;
unsigned long DBUpdateInterval = 5000; //Update DB every 5seconds

// Timer for LCD Display
unsigned long currentDisplayTime;
unsigned long prevDisplayTime=0;
unsigned long DisplayInterval = 3000; // display data on OLED once every 2seconds

//Timer for reading PZEM Data
unsigned long readDataInterval = 1000;
unsigned long currentDataTime;
unsigned long prevDataTime = 0;

// Timer for checking for config updates on firebase: meter reset, switch reset, sync interval
unsigned long lastCheckedUpdate =0;
unsigned long currentCheckedUpdate =0;
unsigned long checkUpdateDuration = 7000;

// Timer for checking for config updates on firebase: meter reset, switch reset, sync interval
unsigned long lastLoadDeactivated =0;
unsigned long currentLoadDeactivated =0;
unsigned long LoadDeactivateDuration = 10000;


bool SerialDebug = true;

void setup() {
  Serial.begin(115200);
  configureActuators();
  setLCD();
  connectWiFi();
  setupNTP();
  connectFirebaseDB(); 
  delay(100);
  getConfigData();  //Unit price and load treshhold
  getUpdatedDataFromDB();  //reset meter status and sync timer
}



void loop() {
  // You can add code to update the values of current, power, energy, and cost here
  readMeterData(); //read data from energy sensor
  //display_data();  //Display data on LCD
  fb_push_get_json(); //log Data to Cloud DB
  display_vip();
  controlLoad();
  checkForUpdates();
}


void configureActuators(){
  pinMode(relay, OUTPUT);
  pinMode(buzzer, OUTPUT);
  //pinMode(redLed, OUTPUT);
  digitalWrite(buzzer, LOW);
  //digitalWrite(redLed, LOW);
  digitalWrite(relay, LOW); //Default is load ON
}

void display_energy_cost(){
    //delay(3000);
    lcd.clear();

    // Set Energy
    lcd.setCursor(0, 0);
    lcd.print(energy_msg);
    lcd.setCursor(7, 0);
    lcd.print(String(energy, 2));

    // Set Cost
    lcd.setCursor(0, 1);
    lcd.print(cost_msg);
    lcd.setCursor(8, 1);
    lcd.print(String(cost, 2));

}

void display_vip(){
    lcd.clear();
    // Set voltage
    if (!isnan(current)) {
    lcd.setCursor(0, 0);
    lcd.print(voltage_msg);
    lcd.setCursor(2, 0);
    lcd.print(voltage);

    // Set Current
    lcd.setCursor(7, 0);
    lcd.print(current_msg);
    lcd.setCursor(9, 0);
    lcd.print(String(current, 2));

     // Set Power Factor
    lcd.setCursor(0, 1);
    lcd.print(factor_msg);
    lcd.setCursor(2, 1);
    lcd.print(String(powerfactor, 2));

    // Set Power
    lcd.setCursor(7, 1);
    lcd.print(power_msg);
    lcd.setCursor(9, 1);
    lcd.print(String(power, 2));
     }
  else{
    lcd.setCursor(2, 0);
    lcd.print("Warning!!!");
    lcd.setCursor(3, 1);
    lcd.print("Overload");
  }

}

void setLCD(){
    lcd.begin();
    //lcd.init();
    lcd.backlight();  // Make sure backlight is on
  
    // Print a message on both lines of the LCD.
    lcd.setCursor(0, 0);  // Set cursor to character 0 on line 0
    lcd.print("SMART METER");
    lcd.setCursor(0, 1);  // Move cursor to character 0 on line 1
    lcd.print("Initializing...");
    delay(2000);
    display_vip();
    //delay(4000);
   // display_energy_cost();
}

//Connecting to WIFI
void connectWiFi(){
    unsigned long wifidelay = 60000; //1 min
    unsigned long lastChecked = 0;
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    Serial.print("Connecting to Wi-Fi");
    while (WiFi.status() != WL_CONNECTED)
    {
       Serial.print(".");
        delay(300);
      } 
      Serial.println();
      Serial.print("Connected with IP: ");
      Serial.println(WiFi.localIP());
      Serial.println();   
}
  
 // Connecting to Firebase
void connectFirebaseDB(){
    config.api_key = API_KEY;
    auth.user.email = USER_EMAIL;
    auth.user.password = USER_PASSWORD;
    config.database_url = DATABASE_URL;
    config.token_status_callback = tokenStatusCallback; // see addons/TokenHelper.h
    Firebase.begin(&config, &auth);

    // Comment or pass false value when WiFi reconnection will control by your code or third party library
    Firebase.reconnectWiFi(true);
    //Firebase.reconnectWiFi(false);
    fbdo.setResponseSize(4096);
    //fbdo.setResponseSize(8192); // Max is 16384 bytes. 
     //WiFi reconnect timeout (interval) in ms (10 sec - 5 min) when WiFi disconnected.
    //config.timeout.wifiReconnect = 10 * 1000;
    //Comment next three lines for annonymous user
     //String base_path = "/userID/";
     String var = "$userId";
     String val = "($userId === auth.uid && auth.token.premium_account === true && auth.token.admin === true)";
     Firebase.RTDB.setReadWriteRules(&fbdo, base_path, var, val, val, DATABASE_SECRET);
}

void readMeterData(){  // Read data every readDataInterval
  currentDataTime = millis();
  if (currentDataTime-prevDataTime >= readDataInterval){
    //Serial.print("Custom Address:");
    //Serial.println(pzem.readAddress(), HEX);
    current = pzem.current();  
    voltage = pzem.voltage();
    power =  pzem.power(); //Power in KW
    energy =  pzem.energy();  //Cumulative energy in KWhr
    //float frequency = pzem.frequency();  //frequency (Hz)
     powerfactor = pzem.pf();  //power factor
    //Price(NGN)  from  ENERGY(KWhr)
    unit_price = configDataValue_float[1];
    cost = energy*unit_price;  //units is Kg
    prevDataTime = millis();
  }
}

void update_data_arrays() {
  time_t now_unixtime = time(nullptr);
   
  //String jsonKeys[7] ={"voltage", "current","power","energy","cost", "unixtime","resetMeter"};
  
  // Update float array
  if (!isnan(current)){
      dataValue_float[0] = voltage;
      dataValue_float[1] = current;
      dataValue_float[2] = power;
      dataValue_float[3] = energy;
      dataValue_float[4] = powerfactor;
      dataValue_float[5] = cost;
  }
  
  

  // Update int array
  dataValue_int[0] = now_unixtime;

  // Update bool array
  dataValue_bool[0] = resetMeter;
  display_vip();

}

void fb_push_get_json(){  //push json data to firebase
  //FirebaseJson json;
      update_data_arrays();
      json.setDoubleDigits(5);  //Number of digits allowed including decimals
      json.setFloatDigits(6);
      //{"voltage", "current","power","energy","cost", "unixtime","resetMeter"};
      for (int i=0; i<6; i++){
        json.add(jsonKeys[i], dataValue_float[i]);
      }

      for (int i=6; i<7; i++){
        json.add(jsonKeys[i], dataValue_int[i-6] );
      }
      
      for (int i=7; i<8; i++){
          json.add(jsonKeys[i],dataValue_bool[i-7] );
      }
      
    if (Firebase.ready()){
          if(Firebase.RTDB.setJSON(&fbdo, dataPath, &json)){
            if (SerialDebug == true){
              Serial.println("Succefully Pushed");
            }
          }
          else{ //data not sent
              if (SerialDebug == true){
                Serial.println(fbdo.errorReason().c_str());
              }
          }
  
    }       //Serial.printf("Update json... %s\n\n", Firebase.RTDB.updateNode(&fbdo, "/test/push/" + String(count), &json) ? "ok" : fbdo.errorReason().c_str());
    int i=0;
}

void getUpdatedDataFromDB(){  // check if meter has been reset 
  
  for (int q=0; q<1; q++){
    if (Firebase.ready()){
    if(Firebase.getBool(fbdo, dataPath+resetDataPath[q])){ 
      if (SerialDebug == true){
        //Serial.println("path:"+ fbdo.dataPath());
        //Serial.println("type:"+ fbdo.dataType());
        //Serial.print("Value: ");
        }
          holdResetData[q] =  fbdo.boolData();
      }
    else{ // if unable to fetch a particular data from DB, then get it from EEPROM
          if (SerialDebug == true){
          Serial.print("Error"+ fbdo.errorReason());
          Serial.println();
          }
    }
    
  }

  }
  resetMeter = holdResetData[0];
  int q=0;
}

void getConfigData() {
  // Loop to get float data from Firebase
  for (int z = 0; z < 2; z++) {
    if (Firebase.ready()) {
      if (Firebase.getFloat(fbdo, configDataPath + configKeyPath[z])) { 
        if (SerialDebug) {
          Serial.println("Path: " + fbdo.dataPath());
          Serial.println("Type: " + fbdo.dataType());
          Serial.print("Value: ");
          Serial.println(fbdo.floatData());
        }
        configDataValue_float[z] = fbdo.floatData();
      } 
      else { // If unable to fetch a particular data from DB, then get it from EEPROM
        if (SerialDebug) {
          Serial.print("Error: " + fbdo.errorReason());
          Serial.println();
        }
        // Add your EEPROM reading logic here if necessary
      }
    }
  }

  // Loop to get int data from Firebase
  for (int z = 2; z < 4; z++) {
    if (Firebase.ready()) {
      if (Firebase.getInt(fbdo, configDataPath + configKeyPath[z])) { 
        if (SerialDebug) {
          Serial.println("Path: " + fbdo.dataPath());
          Serial.println("Type: " + fbdo.dataType());
          Serial.print("Value: ");
          Serial.println(fbdo.intData());
        }
        configDataValue_int[z - 2] = fbdo.intData();
      } 
      else { // If unable to fetch a particular data from DB, then get it from EEPROM
        if (SerialDebug) {
          Serial.print("Error: " + fbdo.errorReason());
          Serial.println();
        }
        // Add your EEPROM reading logic here if necessary
      }
    }
  }
  int z=0;
//String configKeyPath[4]={"loadThreshold/", "unitPrice/", "syncDuration/", "loadDeactivateDuration/" };
  load_threshold= configDataValue_float[0];
  unit_price = configDataValue_float[1];
  DBUpdateInterval = configDataValue_int[0];
  LoadDeactivateDuration = configDataValue_int[1];
  
}


void checkForUpdates(){
  currentCheckedUpdate= millis();
  if ((currentCheckedUpdate-lastCheckedUpdate)>= checkUpdateDuration){
    getUpdatedDataFromDB();
    getConfigData();
    lastCheckedUpdate = millis();
  }

}

void controlLoad(){
  if (deactivate_load == true) {  // load currently deactivated
  currentLoadDeactivated = millis();
  if ((currentLoadDeactivated-lastLoadDeactivated)>= LoadDeactivateDuration){
      digitalWrite (relay, LOW); //switch on  load relay
      digitalWrite (buzzer, LOW);
      deactivate_load = false;
  }
  }

  else{     // deactivate_load = false i.e load is on

    if (current >= load_threshold){
    digitalWrite (relay, HIGH); //switch off  load relay
    digitalWrite (buzzer, HIGH); 
    deactivate_load = true;
    lastLoadDeactivated = millis();
  }
  }
  
}
  
