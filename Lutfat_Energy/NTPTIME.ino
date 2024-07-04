//NTP TIME FUNCTION

// Function to convert time_t to formatted string
String getFormattedTime(time_t timeValue, const char *format) {
  struct tm timeinfo;
  localtime_r(&timeValue, &timeinfo);

  char formatted_time[20]; // Adjust the size based on your format
  strftime(formatted_time, sizeof(formatted_time), format, &timeinfo);

  return String(formatted_time);
}


void setupNTP() { //Set time using internet 
  if (SerialDebug == true){
  Serial.print("Setting time using SNTP...");}
  configTime(TIME_ZONE*3600, 0, "pool.ntp.org", "time.nist.gov");
  
  while (!time(nullptr)) {
    if (SerialDebug == true){
    Serial.print(".");}
    delay(500);
  }
  if (SerialDebug == true){
  Serial.println("done!");}

  struct tm timeinfo;
  if (!getLocalTime(&timeinfo)) {
    if (SerialDebug == true){
    Serial.println("Failed to obtain time info");}
    return;
  }
  if (SerialDebug == true){
  Serial.print("Current time: ");
  Serial.println(asctime(&timeinfo));}

  /*// Format and print the date-time string
  char formattedTime[20]; // Adjust the size based on your format
  strftime(formattedTime, sizeof(formattedTime), "%d/%m/%Y %H:%M", &timeinfo);

  Serial.print("Current formated time: ");
  Serial.println(formattedTime);*/
}


//Get and display current time on OLED 
void displayTime(){
  time_t OLED_now_unixtime = time(nullptr);
  // Format and print the date-time string
  //String formattedTime = getFormattedTime(OLED_now_unixtime, "%d/%m/%Y %H:%M");
  String formattedTime = getFormattedTime(OLED_now_unixtime, "%d/%m %H:%M");
  //Serial.print("Current time: ");
  //Serial.println(formattedTime);
}
