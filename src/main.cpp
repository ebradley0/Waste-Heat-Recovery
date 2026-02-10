#include <Arduino.h>
#include <OneWire.h>
#include <DallasTemperature.h>

#define one_wire_bus 2 // Pin D2


// put function declarations here:
void calc_rpm();
int read_water_level();
void printAddress(DeviceAddress deviceAddress);

volatile float rpm = 0;
unsigned long  now;
unsigned long last;

unsigned int water_sensor_pin = A1;

DeviceAddress temp_sensor_0 = { 0x28, 0xEA, 0x64, 0x71, 0x00, 0x00, 0x00, 0xD1 };
DeviceAddress temp_sensor_1 = { 0x28, 0xD6, 0x55, 0x6E, 0x00, 0x00, 0x00, 0xAA };
OneWire oneWire(one_wire_bus);
DallasTemperature sensors(&oneWire);

void setup() {
  // put your setup code here, to run once:
  // Interrupt Configuration
  Serial.begin(115200);
  // Temp sensor configs

  sensors.begin();
  Serial.print("Devices found: ");
  Serial.println(sensors.getDeviceCount());





  // RPM sensor configs
  pinMode(3, INPUT);
  attachInterrupt(digitalPinToInterrupt(3), calc_rpm, FALLING); // Pin 6 is D3
  delay(1000);
}

void loop() {
  Serial.print("RPM: ");
  Serial.println(rpm);
  Serial.print("Water Level: "); 
  Serial.println(read_water_level());

  //Reading temperatures
  sensors.requestTemperatures();
  Serial.print("Temp sensor 0: ");
  Serial.println(sensors.getTempF(temp_sensor_0));


  Serial.print("Temp sensor 1: ");
  Serial.println(sensors.getTempF(temp_sensor_1));
  
  



  delay(5000);


}

void calc_rpm()
{
  now = micros();
  long deltaT = now - last;
  last = now;
  rpm = (60000000.0) / deltaT; // Converintg 60s to microseconds since deltaT is in terms of micros.
  // revolutions per second = 1 / time since last revolution, so RPM is 60 * rps, or 60 / deltaT.
}

int read_water_level()
{
  int water_level = analogRead(water_sensor_pin);
  return water_level;
}

void printAddress(DeviceAddress deviceAddress) {
  for (uint8_t i = 0; i < 8; i++) {
    if (deviceAddress[i] < 16) Serial.print("0");
    Serial.print(deviceAddress[i], HEX);
  }
}