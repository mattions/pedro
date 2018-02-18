 /*
============================================================================================================
                              PEDRO: Programming Educational Robot
============================================================================================================
title           :pedro_v1.ino
description     :Arduino code for Pedro Petit Robot an open source 3D robotic arm
authors         :Almoutazar Saandi
email           :almoutazar.saandi@gmail.com
date            :2016-2017
============================================================================================================
*/

#include <Servo.h>

Servo servo1;
Servo servo2;
Servo servo3;
Servo servo4;
int msg[5];

int val1 = 0;
int val2 = 0;
int val3 = 0;
int val4 = 0;

int stepSpeed = 10;

byte msgByte_test[1];
byte msgByte[6];

boolean btnPlay = false;
boolean btnRec = false;
boolean btnStop = false;

const int ANGLE_MIN = 0;
const int POS_MIN = 550;
const int ANGLE_MAX = 172; 
int POS_MAX = 2400;

void setup() {
  Serial.begin(9600);

  pinMode (9,OUTPUT);
  digitalWrite (9, HIGH);
  pinMode (10,OUTPUT);
  digitalWrite (10, LOW);

  //pinMode (7,INPUT);
  //pinMode (8,INPUT);
 
  pinMode (12,INPUT);
  pinMode (13,INPUT);
 
  servo1.attach(3);
  servo2.attach(5);
  servo3.attach(6);
  servo4.attach(11);

  delay(1000);
}

void loop () {

/*
  if (digitalRead(12) == true) {
     digitalWrite (9, HIGH);
//     msgByte_test[0]- = 55;  
//     Serial.write(msgByte_test, 1);
   //    Serial.write("hello");
     //int bytesSent = Serial.write("hello");

  } else if (digitalRead(12) == false) {
     digitalWrite (9, LOW);
  }

  if (digitalRead(13) == true) {
     digitalWrite (10, HIGH);
  } else if (digitalRead(13) == false) {
     digitalWrite (10, LOW);
  }

*/
  if (digitalRead(7) == true) {
     digitalWrite (9, HIGH);
       analog_Write();
  } else if (digitalRead(7) == false) {
     digitalWrite (9, LOW);
  }
  if (digitalRead(8) == true) {
     digitalWrite (10, HIGH);
       serialRead();
  } else if (digitalRead(8) == false) {
     digitalWrite (10, LOW);
  }
  
  
}

void analog_Read() {

  val1 = analogRead(5); 
  val1 = map(val1, 0, 1023, 0, 180);  
   
  val2 = analogRead(4); 
  val2 = map(val2, 0, 1023, 0, 180); 

  val3 = analogRead(3); 
  val3 = map(val3, 0, 1023, 0, 180);

  val4 = analogRead(2); 
  val4 = map(val4, 0, 1023, 0, 180); 

  msg[1] = val1;  
  msg[2] = val2;
  msg[3] = val3; 
  msg[4] = val4; 
  
}

void analog_Write() {
  analog_Read(); 
  servo1.write (msg[1]); 
  servo2.write (msg[2]);
  servo3.write (msg[3]);
  servo4.write (msg[4]);
} 

void serialRead() {

    while(Serial.available()>0) {
         Serial.readBytes(msgByte, sizeof(msgByte)); 
         if (msgByte[0] == 1) {          //byte id servo
            servoPosition (servo1, msgByte[1]);
         } else if (msgByte[0] == 2) {
            servoPosition (servo2, msgByte[1]);
         } else if (msgByte[0] == 3) {
            servoPosition (servo3, msgByte[1]);
         } else if (msgByte[0] == 4) {
            servoPosition (servo4, msgByte[1]);
         } else if (msgByte[0] == 9 and msgByte[1] == 1 and msgByte[2] == 1 and msgByte[3] == 0 and msgByte[4] == 3 and msgByte[5] == 1) {
            Serial.print("Hi! Im Pedro");
         }

         if (msgByte[2] == 99) {          //play
            btnPlay = true;
         } else if (msgByte[2] == 88) {   //record
            btnRec = true;
         } else if (msgByte[2] == 77) {   //stop
            btnStop = true;
         }
    }
}

void servoPosition (Servo servo, byte servoAngle) {
  int servoRead = servo.read();
  if (servoRead < servoAngle){
      for (int j = servoRead; j<=servoAngle; j++){
        servo.write(j);
        delay(stepSpeed);
      }
    }
    else if (servoRead > servoAngle){
      for (int j = servoRead; j>=servoAngle; j--){
        servo.write(j);
        delay(stepSpeed);
      }
    }
    else{
      servo.write(angle(servoAngle));
    }
}

int angle(int valeur_angle) { 

        int impuls=0;
        impuls=map(valeur_angle,ANGLE_MIN,ANGLE_MAX,POS_MIN, POS_MAX);
        return impuls;   
}
