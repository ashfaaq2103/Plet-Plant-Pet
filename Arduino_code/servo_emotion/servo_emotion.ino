#include <Servo.h>

// Define the servo objects
Servo servo1;
Servo servo2;

// Define the pins to which the servo motors are connected
const int servoPin1 = 9; // Pin for servo 1
const int servoPin2 = 10; // Pin for servo 2
int IRSensor = 11; // Pin for IR sensor
int completelyWet = 130; // Moisture level indicating completely wet
int completelyDry = 700; // Moisture level indicating completely dry

int startPosLeft = 80; // Initial position for servo 2 (left)
int startPosRight = 90; // Initial position for servo 1 (right)

// Function prototypes
void stop(); // Stop movement function
void run(); // Run movement function
void hello(); // Greeting movement function
void happy(); // Happy movement function
void anger(); // Angry movement function

void processInput(String input); // Function to process serial input

void setup() {
  // Attach the servo objects to the respective pins
  servo1.attach(servoPin1); // Attach servo 1 to pin
  servo2.attach(servoPin2); // Attach servo 2 to pin
  pinMode(IRSensor, INPUT); // Set IR sensor pin as INPUT
  Serial.begin(9600); // Initialize serial communication
}

// Function to read moisture sensor value
int getMoistSensorReading() {
  int averageSensorVal = 0;

  // Take 10 readings and calculate the average
  for (int i = 0; i < 10; i++) {
    int sensorValue = analogRead(A1); // Read analog pin A1
    averageSensorVal += sensorValue;
    delay(10); // Add a small delay between readings for stability
  }

  averageSensorVal = averageSensorVal / 10;
  return averageSensorVal;
}

// Function to check serial input
void checkSerialInput() {
  int previousMoisture = -1; // Initialize to an invalid value
  int currentMoisture = getMoistSensorReading();
  if (currentMoisture != previousMoisture || sensorStatus == 1) {
   // Send data only if moisture changes or IR sensor detects something
    String message = "moisture:" + String(currentMoisture);
    Serial.println(message);
    previousMoisture = currentMoisture;
  }
}

// Main loop function
void loop() {
  checkSerialInput(); // Check for changes in moisture or IR sensor status
  if (Serial.available()) {
    String input = Serial.readString(); // Read the entire string
    input.trim(); // Remove leading/trailing whitespaces
    processInput(input); // Process the input
  }
}

// Function to process serial input commands
void processInput(String input) {
  // Based on the input, call the corresponding function
  if (input == "anger") {
    anger();
  } else if (input == "run") {
    run();
  } else if (input == "hello") {
    hello();
  } else if (input == "happy") {
    happy();
  } else if (input == "stop") {
    stop();
  } else if (input == "sad") {
    sad();
  }
}

// Function to stop the movement of both servos
void stop() {
  servo1.write(startPosRight); // Set servo 1 to startPosRight
  servo2.write(startPosLeft); // Set servo 2 to startPosLeft
}

// Function for running movement
void run() {
  for (int i = 0; i < 8; i++) {
    for (int pos = 0; pos <= 130; pos += 1) {
      servo1.write(pos);
      servo2.write(pos);
      delay(2);
    }
    for (int pos = 130; pos >= 0; pos -= 1) {
      servo1.write(pos);
      servo2.write(pos);
      delay(5);
    }
  }
  stop(); // Stop after running
}

// Function for sad movement
void sad() {
  stop();
  int count = 0;
  for (int pos = startPosRight; pos <= 175; pos += 1) {
    servo1.write(pos);
    delay(30);
  }
  for (int pos = 175; pos >= startPosRight; pos -= 1) {
    servo1.write(pos);
    int posLeft = (count);
    delay(35);
  }
  stop();
  delay(3000);
}

// Function for angry movement
void anger() {
  stop();
  for (int i = 0; i < 15; i++) {
    for (int pos = 120; pos <= 170; pos += 1) {
      servo1.write(pos);
      servo2.write(pos - 120);
      delay(5);
    }
    for (int pos = 170; pos >= 120; pos -= 1) {
      servo1.write(pos);
    }
  }
  stop(); // Stop after anger movement
}

// Function for greeting movement
void hello() {
  for (int i = 0; i < 3; i++) {
    for (int pos = 120; pos <= 200; pos += 1) {
      servo1.write(pos);
      delay(5);
    }
    for (int pos = 200; pos >= 120; pos -= 1) {
      servo1.write(pos);
      delay(5);
    }
  }
  stop();
  delay(3000);
}

// Function for happy movement
void happy() {
  stop();
  int count = 0;
  for (int pos = startPosRight; pos <= 200; pos += 1) {
    servo1.write(pos);
    servo2.write(0);
  }
  for (int pos = 200; pos >= startPosRight; pos -= 1) {
    servo1.write(pos);
    int posLeft = (count);
    servo2.write(posLeft);
    delay(25);
    if (pos % 2 == 0) {
      count += 1;
    }
  }
  stop();
  delay(3000);
}
