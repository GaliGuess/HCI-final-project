#include <CapacitiveSensor.h>

// Data transfer to pySerial options
char CMD_START_TRANSMISSION = 'G';
char CMD_END_TRANSMISSION = 'X';
char SERIAL_END_TRANSMISSION = 'E';
bool sending_data = true;
char serial_input;

// LED options
char CMD_LED_ON = 'I';
char CMD_LED_OFF = 'O';
int led_pin = A0;
int led_on_val = 255;
int led_off_val = 0;

bool SERIAL_PLOTTER = false;

const int numSensors = 8;
int cs_samples = 80;
int sensor_calibration_time = 0xFFFFFFFF;
int delay_time = 50; 

CapacitiveSensor* sensors[numSensors];
long sensorValues[numSensors];

// signal smoothing parameters (sends the sensors' average instead of current value):
// https://www.arduino.cc/en/Tutorial/Smoothing
//
bool SMOOTHING_ON = true;
const int numReadings = 10;                // the number of sensor readings to average
long readings[numSensors][numReadings];    // the readings from the analog input
int readIndex = 0;                         // the index of the current reading
long total[numSensors];                    // the running total
long average[numSensors];                  // the average

int delay_time_readings = 1;


// Initialize all capacitive sensors
void init_sensors() {
  sensors[0] = new CapacitiveSensor(13, 3);
  sensors[1] = new CapacitiveSensor(13, 9);
  sensors[2] = new CapacitiveSensor(13, 11);
  sensors[3] = new CapacitiveSensor(13, 2);
  sensors[4] = new CapacitiveSensor(13, 5);
  sensors[5] = new CapacitiveSensor(13, 12);
  sensors[6] = new CapacitiveSensor(13, 6);
  sensors[7] = new CapacitiveSensor(13, 8);

  for (int sensor_idx = 0; sensor_idx < numSensors; sensor_idx++) {
    sensors[sensor_idx]->set_CS_AutocaL_Millis(sensor_calibration_time);
  }
}


void setup() {
  Serial.begin(9600);

  init_sensors();
  pinMode(led_pin, OUTPUT);
  analogWrite(led_pin, led_on_val);

  for (int sensor_idx = 0; sensor_idx < numSensors; sensor_idx++) {
    sensorValues[sensor_idx] = 0;

    if (SMOOTHING_ON) {
      total[sensor_idx] = 0;
      average[sensor_idx] = 0;
      for (int thisReading = 0; thisReading < numReadings; thisReading++) {
        readings[sensor_idx][thisReading] = 0;
      }
    }
  }
}


void loop() {

  if (SMOOTHING_ON) {
    
    for (int i = 0; i < numSensors; i++) {
      
      // subtract the last reading:
      total[i] = total[i] - readings[i][readIndex];
      
      // read from the sensor:
      readings[i][readIndex] = sensors[i]->capacitiveSensor(cs_samples);
      
      // add the reading to the total:
      total[i] = total[i] + readings[i][readIndex];

      // calculate the average:
      average[i] = total[i] / numReadings;

      sensorValues[i] = average[i];
    }
    
    // advance to the next position in the array:
    readIndex = readIndex + 1;
  
    // if we're at the end of the array...
    if (readIndex >= numReadings) {
      // ...wrap around to the beginning:
      readIndex = 0;
    }
        
    delay(delay_time_readings);
  }

  // Read input commands from serial
  if (Serial.available() > 0)
  {
    serial_input = Serial.read();
    if (serial_input == CMD_START_TRANSMISSION)
    {
      sending_data = true;
    }
    else if (serial_input == CMD_END_TRANSMISSION) 
    {
      sending_data = false;
    }
    else if (serial_input == CMD_LED_ON)
    {
      analogWrite(led_pin, led_on_val);
    }
    else if (serial_input == CMD_LED_OFF)
    {
      analogWrite(led_pin, led_off_val);
    }
  }
  
  // If data is sent to the serial plotter instead of pySerial, this overwrites the need for a command to be sent
  if (SERIAL_PLOTTER) {
    sending_data = true;
  }

  // Actual data sending
  if (sending_data)
  { 
    if (!SMOOTHING_ON) 
    {
      for (int i = 0; i < numSensors; i++) {
        sensorValues[i] = sensors[i]->capacitiveSensor(cs_samples);
      }
    }
    
    // printing sensor data to serial in python or serial plotter format
    if (!SERIAL_PLOTTER) 
    {
      printToPython();
    }
    else 
    {
      printToSerialPlotter();
    }
    
    delay(delay_time);
  }
}

// prints the sensor data once to pySerial
void printToPython() {
  for (int i = 0; i < numSensors; i++) {
    Serial.println(sensorValues[i]);
  }
  Serial.println(SERIAL_END_TRANSMISSION);
  sending_data = false;
}

// prints the data in format for arduino serial plotter
void printToSerialPlotter() {
  for (int i = 0; i < numSensors - 1; i++) {
      Serial.print(sensorValues[i]);
      Serial.print(",");
  }
  Serial.println(sensorValues[numSensors - 1]);
}


