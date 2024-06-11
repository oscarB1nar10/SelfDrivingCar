#include <SoftwareSerial.h>

// Motor A
int motorA1 = 2;
int motorA2 = 3;
int enableA = 9; // Use a PWM pin

// Motor B
int motorB1 = 4;
int motorB2 = 5;
int enableB = 10; // Use a PWM pin

// Bluetooth Module Pins
int rxPin = 0; // Connect to TX of the Bluetooth
int txPin = 1; // Connect to RX of the Bluetooth

// Initialize SoftwareSerial for Bluetooth
SoftwareSerial bluetooth(rxPin, txPin);

unsigned long lastCommandTime;
const unsigned long commandTimeout = 100; // Time in milliseconds to wait for a new command
bool isMoving = false;

void setup() {
  // Set the motor pins as outputs
  pinMode(motorA1, OUTPUT);
  pinMode(motorA2, OUTPUT);
  pinMode(enableA, OUTPUT);
  pinMode(motorB1, OUTPUT);
  pinMode(motorB2, OUTPUT);
  pinMode(enableB, OUTPUT);

  // Start serial communication with the Bluetooth module
  bluetooth.begin(9600);
  Serial.begin(9600); // Start serial for debugging

  lastCommandTime = millis();
}

void loop() {
  if (bluetooth.available()) {
    char command = bluetooth.read();
    lastCommandTime = millis();
    isMoving = true;
    controlMotors(command);
  }
  else if (isMoving && millis() - lastCommandTime >= commandTimeout) {
    // If no command has been received for a while, stop the motors
    stopMotors();
    isMoving = false;
  }
}

void controlMotors(char command) {
  switch (command) {
    case 'f':
      moveForward();
      break;
    case 'b':
      moveBackward();
      break;
    case 'l':
      turnLeft();
      break;
    case 'r':
      turnRight();
      break;
  }
}

void moveForward() {
  digitalWrite(motorA1, HIGH);
  digitalWrite(motorA2, LOW);
  digitalWrite(motorB1, HIGH);
  digitalWrite(motorB2, LOW);
  analogWrite(enableA, 255);
  analogWrite(enableB, 255);
}

void moveBackward() {
  digitalWrite(motorA1, LOW);
  digitalWrite(motorA2, HIGH);
  digitalWrite(motorB1, LOW);
  digitalWrite(motorB2, HIGH);
  analogWrite(enableA, 255);
  analogWrite(enableB, 255);
}

void turnLeft() {
  digitalWrite(motorA1, LOW);
  digitalWrite(motorA2, HIGH);
  digitalWrite(motorB1, HIGH);
  digitalWrite(motorB2, LOW);
  analogWrite(enableA, 255);
  analogWrite(enableB, 255);
}

void turnRight() {
  digitalWrite(motorA1, HIGH);
  digitalWrite(motorA2, LOW);
  digitalWrite(motorB1, LOW);
  digitalWrite(motorB2, HIGH);
  analogWrite(enableA, 255);
  analogWrite(enableB, 255);
}

void stopMotors() {
  digitalWrite(motorA1, LOW);
  digitalWrite(motorA2, LOW);
  digitalWrite(motorB1, LOW);
  digitalWrite(motorB2, LOW);
  analogWrite(enableA, 0);
  analogWrite(enableB, 0);
}
