// Pin numbers definition
const int motorForwardLeft = 5; // Pin for left motor forward
const int motorBackLeft = 4; // Pin for left motor backward
const int motorForwardRight = 2; // Pin for right motor forward
const int motorBackRight = 3; // Pin for right motor backward
const int trigPinFront = A1; // Pin for front ultrasonic sensor trigger
const int echoPinFront = A2; // Pin for front ultrasonic sensor echo
const int trigPinLeft = 8; // Pin for left ultrasonic sensor trigger
const int echoPinLeft = 9; // Pin for left ultrasonic sensor echo
const int trigPinRight = 10; // Pin for right ultrasonic sensor trigger
const int echoPinRight = 11; // Pin for right ultrasonic sensor echo
int IRSensor = 53;  // Pin for IR sensor
const int motorEnableLeft = 13; // Pin for enabling left motor
const int motorEnableRight = 12; // Pin for enabling right motor
#define DO_PIN_REAR A0  // Pin for rear sensor

// Variables for the Motors
const int delayTime = 150; // Delay time for motor movement
const int leftMotorSpeed = 200; // Speed for the left motor
const int rightMotorSpeed = 175; // Speed for the right motor

// Variables for Ultrasonic Sensors
long durationFront; // Duration for front ultrasonic sensor
int distanceFront; // Distance measured by front ultrasonic sensor
long durationLeft; // Duration for left ultrasonic sensor
int distanceLeft; // Distance measured by left ultrasonic sensor
int lightState1; // State of light sensor
long durationRight; // Duration for right ultrasonic sensor
int distanceRight; // Distance measured by right ultrasonic sensor
const int minFrontDistance = 30; // Minimum distance threshold for front sensor
const int minSideDistance = 20; // Minimum distance threshold for side sensors
const int stuckDistance = 15; // Distance indicating the robot is stuck

// Function to check if IR sensor detects something
int checkIR() {
  int sensorStatus = digitalRead(IRSensor); // Read IR sensor status
  if (sensorStatus == 1) {
    return 1; // Return 1 if sensor detects something
  } else {
    return 0; // Return 0 if sensor detects nothing
  }
}

void checkSerialInput() {
  bool lifted = false;  
  int sensorStatus = checkIR();
  String message=""; 
  delay(1000); 
  if (sensorStatus == 1) {
    message += ",lifted";  // Append "lifted" if IR sensor detects something
    lifted = true; 
  }
  else
  {
    lifted = false; 
    message += ",none";
  }
  Serial.println(message);
  if (lifted == true)
  {
    delay(5000); 
  }
}

// Function to stop the car
void stopCar() {
  digitalWrite(motorForwardLeft, LOW);
  digitalWrite(motorBackLeft, LOW);
  digitalWrite(motorForwardRight, LOW);
  digitalWrite(motorBackRight, LOW);
}

// Function to move the car forward at full speed
void goForwardFull() {
  digitalWrite(motorForwardLeft, HIGH);
  digitalWrite(motorBackLeft, LOW);
  digitalWrite(motorForwardRight, HIGH);
  digitalWrite(motorBackRight, LOW);
  analogWrite(motorEnableLeft, leftMotorSpeed);
  analogWrite(motorEnableRight, rightMotorSpeed);
}

// Function to turn the car left
void goLeft() {
  digitalWrite(motorForwardLeft, LOW);
  digitalWrite(motorBackLeft, LOW);
  digitalWrite(motorForwardRight, HIGH);
  digitalWrite(motorBackRight, LOW);
}

// Function to turn the car right
void goRight() {
  digitalWrite(motorForwardLeft, HIGH);
  digitalWrite(motorBackLeft, LOW);
  digitalWrite(motorForwardRight, LOW);
  digitalWrite(motorBackRight, LOW);
}

// Function to move the car backward
void goBack() {
  digitalWrite(motorForwardLeft, LOW);
  digitalWrite(motorBackLeft, HIGH);
  digitalWrite(motorForwardRight, LOW);
  digitalWrite(motorBackRight, HIGH);
}

// Function to read sensor values
void sensorRead() {
  // Read front sensor value
  digitalWrite(trigPinFront, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPinFront, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPinFront, LOW);
  durationFront = pulseIn(echoPinFront, HIGH);
  distanceFront = durationFront * 0.034 / 2;

  // Read left sensor value
  digitalWrite(trigPinLeft, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPinLeft, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPinLeft, LOW);
  durationLeft = pulseIn(echoPinLeft, HIGH);
  distanceLeft = durationLeft * 0.034 / 2;

  // Read right sensor value
  digitalWrite(trigPinRight, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPinRight, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPinRight, LOW);
  durationRight = pulseIn(echoPinRight, HIGH);
  distanceRight = durationRight * 0.034 / 2;
  lightState1 = analogRead(DO_PIN_REAR); // Read light sensor value
}

// Setup function
void setup() {
  // Initialize serial communication
  Serial.begin(19200);
  pinMode(DO_PIN_REAR, INPUT);
  pinMode(motorForwardLeft, OUTPUT);
  pinMode(motorBackLeft, OUTPUT);
  pinMode(motorForwardRight, OUTPUT);
  pinMode(motorBackRight, OUTPUT);
  pinMode(trigPinFront, OUTPUT);
  pinMode(echoPinFront, INPUT);
  pinMode(trigPinLeft, OUTPUT);
  pinMode(echoPinLeft, INPUT);
  pinMode(trigPinRight, OUTPUT);
  pinMode(echoPinRight, INPUT);
}

// Function for autonomous movement away from light
void autonomous_movement_away_from_light() {
  sensorRead();
  while (lightState1 <=150 ) {
    sensorRead();
    if ((distanceFront <= minFrontDistance) || (distanceLeft <= minSideDistance) || (distanceRight <= minSideDistance)) {
      if ((distanceLeft < stuckDistance) || (distanceRight < stuckDistance) || (distanceFront < stuckDistance) ) {
        goBack();
        delay(1.5*delayTime);
      } else if ((distanceFront <= minFrontDistance) && (distanceLeft <= minSideDistance) && (distanceRight <= minSideDistance)) {
        goBack();
        delay(1.5*delayTime);   
      } else if (distanceLeft > distanceRight ) {
        goLeft();
        delay(delayTime);     
      } else if (distanceLeft <= distanceRight) {
        goRight();
        delay(delayTime);  
      } else
        goForwardFull();   
    } else
      goForwardFull();
  }
  stopCar(); 
}

// Function for autonomous movement towards light
void autonomous_movement_get_light() {
  sensorRead();
  while (lightState1 > 150 ) {
    sensorRead();
    if ((distanceFront <= minFrontDistance) || (distanceLeft <= minSideDistance) || (distanceRight <= minSideDistance)) {
      if ((distanceLeft < stuckDistance) || (distanceRight < stuckDistance) || (distanceFront < stuckDistance) ) {
        goBack();
        delay(1.5*delayTime);
      } else if ((distanceFront <= minFrontDistance)  && (distanceLeft <= minSideDistance) && (distanceRight <= minSideDistance)) {
        goBack();
        delay(1.5*delayTime);     
      } else if (distanceLeft > distanceRight ) {
        goLeft();
        delay(delayTime);      
      } else if (distanceLeft <= distanceRight) {
        goRight();
        delay(delayTime);   
      } else
        goForwardFull();   
    } else
      goForwardFull();
  }
  stopCar(); 
}

// Function to water the plant
void water() {
  for (int y = 0; y < 3; y++) {
    for (int i = 0; i < 5; i++) {
      digitalWrite(motorForwardLeft, HIGH);
      digitalWrite(motorBackLeft, LOW);
      digitalWrite(motorForwardRight, LOW);
      digitalWrite(motorBackRight, HIGH);
      analogWrite(motorEnableLeft, leftMotorSpeed);
      analogWrite(motorEnableRight, rightMotorSpeed);
      delay(300);
       digitalWrite(motorForwardLeft, LOW);
      digitalWrite(motorBackLeft, HIGH);
      digitalWrite(motorForwardRight, HIGH);
      digitalWrite(motorBackRight, LOW);
      analogWrite(motorEnableLeft, leftMotorSpeed);
      analogWrite(motorEnableRight, rightMotorSpeed);
      delay(300);
    }
    stopCar(); 
    delay(5000); 
  }
}

// Function to run the car
void run() {
  for (int i = 0; i < 7; i++) {
    digitalWrite(motorForwardLeft, HIGH);
    digitalWrite(motorBackLeft, LOW);
    digitalWrite(motorForwardRight, LOW);
    digitalWrite(motorBackRight, HIGH);
    analogWrite(motorEnableLeft, leftMotorSpeed);
    analogWrite(motorEnableRight, rightMotorSpeed);
    delay(500);
    digitalWrite(motorForwardLeft, LOW);
    digitalWrite(motorBackLeft, HIGH);
    digitalWrite(motorForwardRight, HIGH);
    digitalWrite(motorBackRight, LOW);
    analogWrite(motorEnableLeft, leftMotorSpeed);
    analogWrite(motorEnableRight, rightMotorSpeed);
    delay(500);
  }
  stopCar(); 
  delay(5000); 
}

// Function to greet
void greet() {
   digitalWrite(motorForwardLeft, HIGH);
   digitalWrite(motorBackLeft, LOW);
   digitalWrite(motorForwardRight, LOW);
   digitalWrite(motorBackRight, HIGH);
   analogWrite(motorEnableLeft, leftMotorSpeed);
   analogWrite(motorEnableRight, rightMotorSpeed);
   delay(350);
   digitalWrite(motorForwardLeft, LOW);
   digitalWrite(motorBackLeft, HIGH);
   digitalWrite(motorForwardRight, HIGH);
   digitalWrite(motorBackRight, LOW);
   analogWrite(motorEnableLeft, leftMotorSpeed);
   analogWrite(motorEnableRight, rightMotorSpeed);
   delay(350);
   stopCar(); 
   delay(5000); 
}

// Main loop function
void loop() {
  checkSerialInput();
  if (Serial.available()) {
    String input = Serial.readString();  // Read the entire string
    input.trim(); // Remove leading/trailing whitespaces
    processInput(input); // Process the input
  }
}

// Function to process serial input
void processInput(String input) {
  // Based on the input, call the corresponding function
  if (input == "play") {
    run();
  } else if (input == "greet") {
    greet();
  } else if (input == "water") {
    water();
  } else if (input == "light") {
    autonomous_movement_get_light();
  } else if (input == "nolight") {
    autonomous_movement_away_from_light();
  }
}
