//============================================================================================================
//                              PEDRO : Programming Educational Robot
//============================================================================================================
//title           :pedro.ino
//description     :Arduino code for Pedro Petit Robot an open source 3D robotic arm, with serial USB control
//email           :pedropetitrobot@gmail.com
//date            :2016-2017
//version         :1.0
//============================================================================================================

#include <Servo.h>
#include <EEPROM.h>
// Servo declarations
Servo servo1;
Servo servo2;
Servo servo3;
Servo servo4;
int addr = 0;
int recOK = 0;
int posOne, posTwo, posThree, posFour, posFive;
int posOne1, posTwo1, posThree1, posFour1, posFive1;
/*
int posServo1[100];
int posServo2[100];
int posServo3[100];
int posServo4[100];
*/
byte msgByte[6];
String msgString = "";
int msg[5];
boolean replaying = false;
boolean recording = false;
int stepSpeed = 10; //Change this to fo faster!
int state = 0;
boolean btnPlay = false;
boolean btnRec = false;
boolean btnStop = false;
const int ANGLE_MIN = 0; // angle position MIN en degrés
const int POS_MIN = 550; // largeur impulsion pour position ANGLE_MIN degrés du servomoteur
                         // POS_MIN=550 pour ANGLE_MIN=0 avec un futaba S3003
const int ANGLE_MAX = 172; // angle position MAX en degrés
int POS_MAX = 2400; // largeur impulsion pour position ANGLE_MAX degrés du servomoteur
int button_1 = LOW;
int button_2 = LOW;
int btnRepeat = LOW;
int old_btnRepeat = LOW;
bool serialUsed = false;
int val1 = 0;
int val2 = 0;
int val3 = 0;
int val4 = 0;
boolean inRecord = false;
boolean serialStop = false;
void setup() {
  Serial.begin(9600);
  pinMode (9,OUTPUT);
  digitalWrite (9, LOW);
  pinMode (10,OUTPUT);
  digitalWrite (10, LOW);
  pinMode (12,INPUT);
  pinMode (13,INPUT);
  servo1.attach(3);
  servo2.attach(5);
  servo3.attach(6);
  servo4.attach(11); 
 
  analog_Write();  
  goHome();
}
void loop() {
  //analog_Write();
  serialRead();
  button_1 = digitalRead(12);
  button_2 = digitalRead(13);
  if (digitalRead(12) == true and inRecord == false) {
    inRecord = true;
     record();
     if (digitalRead(13) == true)
     { 
        addr = 0;
        digitalWrite (9, HIGH); //jaune
        //EEPROM.write(addr, 254);
        //addr = 1;
        while (addr <= 1020) {
          digitalWrite (9, HIGH); //jaune
          //posServo1[addr] = 255;
          //posServo2[addr] = 255;
          //posServo3[addr] = 255;
          //posServo4[addr] = 255;
          EEPROM.write(addr, 255);
          addr++;  
         }
        addr = 0; 
        //addr = 1;
        digitalWrite (9, HIGH);
        delay(100);
        digitalWrite (9, LOW);
        delay(100);
        digitalWrite (9, HIGH);
        delay(100);
        digitalWrite (9, LOW);
        record();
    }
  }
  if (digitalRead(12) == false) {
      inRecord = false;
  }
/*
  if (digitalRead(12) == true) {
    record();
  }
  */
  if (digitalRead(13) == HIGH and digitalRead(12) == LOW) {
      addr = 0;
      //recOK = EEPROM.read(addr);
      //if (recOK == 254) {
          digitalWrite (10, HIGH); //rouge
         // addr = 1;
          replaying = true;
          replay();
     // }
  } else if (button_2 == LOW) {
      digitalWrite (10, LOW);
  }
      
  /*
  if (button_1 == HIGH) {
      
      if (addr == 0) {
      
      digitalWrite (9, HIGH); //jaune
      EEPROM.write(addr, 254);
      addr = 1;
      while (addr <= 1020) {
          digitalWrite (9, HIGH); //jaune
          EEPROM.write(addr, 255);
          addr++;  
       }
      addr = 1;
      }
      recording = true;
      record();
  } else if (button_1 == LOW) {
      digitalWrite (9, LOW);
  }
  if (button_2 == HIGH) {
      digitalWrite (10, HIGH); //rouge
      recOK = EEPROM.read(addr);
      if (recOK == 254) {
          replaying = true;
          replay();
      }
  } else if (button_2 == LOW) {
      digitalWrite (10, LOW);
  }
  
 ////////////////////////
  if (btnRec) {
      digitalWrite (9, HIGH); //jaune
      EEPROM.write(addr, 254);
      recording = true;
      record();
      btnRec = false;
  }  
  if (btnPlay) {
      digitalWrite (10, HIGH); //rouge
      recOK = EEPROM.read(addr);
      if (recOK == 254) {
          replaying = true;
          replay();
      }
      btnPlay = false;
  } 
  */  
}
void repeat() {
  btnRepeat = digitalRead(13);; //stop le robot durant un mode replay
  if ((btnRepeat == HIGH) and (old_btnRepeat == LOW)) {
    if (state == 2) {
      state = 1; //repeat one time
    } else { 
      state++;   //repeat
    }
  }
  old_btnRepeat = btnRepeat;
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
void record() {
  
  //while (recording)
  //  {
  digitalWrite (9, HIGH);
  delay(100);
  digitalWrite (9, LOW);
  
  analog_Read();
  //serialRead();
  
  servo1.write (angle(msg[1]));
  //posServo1[addr] = msg[1];
  Serial.print("record servo1 =");Serial.println(msg[1]);
  EEPROM.write(addr, msg[1]);
  addr++; 
   
  servo2.write (angle(msg[2]));
  //posServo2[addr] = msg[2];      
  EEPROM.write(addr, msg[2]);
  addr++;
  
  servo3.write (angle(msg[3]));
  //posServo3[addr] = msg[3];
  EEPROM.write(addr, msg[3]);
  addr++;
  
  servo4.write (angle(msg[4]));
  //posServo4[addr] = msg[4];
  EEPROM.write(addr, msg[4]);
  addr++;
  if (addr >= 1020)
      {
        digitalWrite (10, LOW);
        digitalWrite (9, HIGH);
        delay (500);
        digitalWrite (9, LOW);
        delay (500);
        digitalWrite (9, HIGH);
        delay (500);
        digitalWrite (9, LOW);
        //EEPROM.write(addr, 255);
        addr = 0;
        recording = false;
        goHome();
      }

   inRecord = false;
} 
void analog_Write() {
  analog_Read(); 
  
  servo1.write (msg[1]); 
  servo2.write (msg[2]);
  servo3.write (msg[3]);
  servo4.write (msg[4]);
} 
void goHome() {
  
  analog_Read();
  goSomeWhere(val1, val2, val3, val4);
}
void goSomeWhere(int value1, int value2, int value3, int value4){
  int servo1Read = servo1.read();
  int servo2Read = servo2.read();
  int servo3Read = servo3.read();
  int servo4Read = servo4.read();
  if (servo1Read < value1){
      for (int j = servo1Read; j<=value1; j++){
        servo1.write(j);
        delay(stepSpeed);
      }
    }
    else if (servo1Read > value1){
      for (int j = servo1Read; j>=value1; j--){
        servo1.write(j);
        delay(stepSpeed);
      }
    }
    else{
      servo1.write(angle(value1));
    }
    
  if (servo2Read < value2){
      for (int j = servo2Read; j<=value2; j++){
        servo2.write(angle(j));
        delay(stepSpeed);
      }
    }
    else if (servo2Read > value2){
      for (int j = servo2Read; j>=value2; j--){
        servo2.write(angle(j));
        delay(stepSpeed);
      }
    }
    else{
      servo2.write(angle(value2));
    }
  if (servo3Read < value3){
      for (int j = servo3Read; j<=value3; j++){
        servo3.write(angle(j));
        delay(stepSpeed);
      }
    }
    else if (servo3Read > value3){
      for (int j = servo3Read; j>=value3; j--){
        servo3.write(j);
        delay(stepSpeed);
      }
    }
    else{
      servo3.write(value3);
    }
  if (servo4Read < value4){
      for (int j = servo4Read; j<=value4; j++){
        servo4.write(angle(j));
        delay(stepSpeed);
      }
    }
    else if (servo4Read > value4){
      for (int j = servo4Read; j>=value4; j--){
        servo4.write(j);
        delay(stepSpeed);
      }
    }
    else{
      servo4.write(value4);
    }
}
void goReplay(){
  addr = 0;
  /*
  posOne = posServo1[addr];
  posTwo = posServo2[addr];
  posThree = posServo3[addr];
  posFour = posServo3[addr];
*/
   
  posOne = EEPROM.read(addr);
  addr++;
  posTwo = EEPROM.read(addr);
  addr++;
  posThree = EEPROM.read(addr);
  addr++;
  posFour = EEPROM.read(addr);
 
  goSomeWhere(posOne, posTwo, posThree, posFour);
}
void replay() { 
  goReplay();
  // Start playback
  addr = 0;
    
  int servo1Saved = servo1.read();
  int servo2Saved = servo2.read();
  int servo3Saved = servo3.read();
  int servo4Saved = servo4.read();
  int i = 0;
  
  while (replaying) { 
    
      //repeat();
      if (digitalRead(13) == HIGH or serialStop == true or i == 1) {
        i = 0;
        digitalWrite (10, HIGH);
        delay (500);
        digitalWrite (10, LOW);
        delay (500);
        digitalWrite (10, HIGH);
        delay (500);
        digitalWrite (10, LOW);
        goHome();
        addr = 0;
        replaying = false;
        serialStop = false;
        break;
      }
      if ((posOne == 255) or (posOne1 == 255) or (posTwo == 255) or (posTwo1 == 255) or (posThree == 255) or (posThree1 == 255) or (posFour == 255) or (posFour1 == 255))
      {
        Serial.println("***********************");
        /*
        posOne = posServo1[addr-1];
        posOne1 = posServo1[0];
        posTwo = posServo2[addr-1];
        posTwo1 = posServo2[0];
        posThree = posServo3[addr-1];
        posThree1 = posServo3[0];
        posFour = posServo4[addr-1];
        posFour1 = posServo4[0];
        */
        
        posOne = EEPROM.read(addr-4);
        posOne1 = EEPROM.read(0);
        addr++;
        posTwo = EEPROM.read(addr-4);
        posTwo1 = EEPROM.read(1);
        addr++;
        posThree = EEPROM.read(addr-4);
        posThree1 = EEPROM.read(2);
        addr++;
        posFour = EEPROM.read(addr-4);
        posFour1 = EEPROM.read(3);
        
        addr = 0;
      } else {
        /*
        posOne = posServo1[addr];
        posOne1 = posServo1[addr+1];
        posTwo = posServo2[addr];
        posTwo1 = posServo2[addr+1];
        posThree = posServo3[addr];
        posThree1 = posServo3[addr+1];
        posFour = posServo4[addr];
        posFour1 = posServo4[addr+1];
        addr++;
        */
        
        posOne = EEPROM.read(addr);
        posOne1 = EEPROM.read(addr+4);
        addr++;
        posTwo = EEPROM.read(addr);
        posTwo1 = EEPROM.read(addr+4);
        addr++;
        posThree = EEPROM.read(addr);
        posThree1 = EEPROM.read(addr+4);
        addr++;
        posFour = EEPROM.read(addr);
        posFour1 = EEPROM.read(addr+4);
        addr++;
        
      }
      if ((posOne != 255) and (posOne1 != 255)) {
        
        Serial.print("#replay posOne =");Serial.println(posOne);
        Serial.print("#replay posOne1 =");Serial.println(posOne1);
        
      // Step from one recording to the next for each servo
      if ((posOne1 - posOne) > 0)
      {
        for (int i = posOne; i <= posOne1; i++)
        {
          servo1.write(i);
          delay(stepSpeed);
        }
      }   
      else if ((posOne1 - posOne) < 0)
      {
        for (int i = posOne; i >= posOne1; i--)
        {
          servo1.write(i);
          delay(stepSpeed);
        }
      }
      }
      if ((posTwo != 255) and (posTwo1 != 255)) {
      if ((posTwo1 - posTwo) > 0)
      {
        for (int i = posTwo; i <= posTwo1; i++)
        {
          servo2.write(i);
          delay(stepSpeed);
        }
      }   
      else if ((posTwo1 - posTwo) < 0)
      {
        for (int i = posTwo; i >= posTwo1; i--)
        {
          servo2.write(i);
          delay(stepSpeed);
        }
      }
      }
      if ((posThree != 255) and (posThree1 != 255)) {
      if ((posThree1 - posThree) > 0)
      {
        for (int i = posThree; i <= posThree1; i++)
        {
          servo3.write(i);
          delay(stepSpeed);
        }
      }   
      else if ((posThree1 - posThree) < 0)
      {
        for (int i = posThree; i >= posThree1; i--)
        {
          servo3.write(i);
          delay(stepSpeed);
        }
      }
      }
      if ((posFour != 255) and (posFour1 != 255)) {
      if ((posFour1 - posFour) > 0)
      {
        for (int i = posFour; i <= posFour1; i++)
        {
          servo4.write(i);
          delay(stepSpeed);
        }
      }   
      else if ((posFour1 - posFour) < 0)
      {
        for (int i = posFour; i >= posFour1; i--)
        {
          servo4.write(i);
          delay(stepSpeed);
        }
      }
      }
      i=i+1;
      
    } // end loop while
}
void writePosServo(int pos, int numServo) {
  if (numServo == 1) {
     msg[1] = pos;
  } else if (numServo == 2) {
     msg[2] = pos;
  } else if (numServo == 3) {
     msg[3] = pos;
  } else if (numServo == 4) {
     msg[4] = pos;
  }
}    
void servoPosition(Servo servo, byte servoDirection, int numServo) {
            int servoRead = servo.read();
            if (servoDirection == 11) {       // byte servo angle +1: increase
               if (servoRead >= 0 and servoRead + 3 < 180) {
                   servo.write (int(servoRead) + 3); 
                   writePosServo(int(servoRead) + 3, numServo);
                   //delay(25);
               }
            } else if (servoDirection == 22) { // byte servo angle -1: decrease
               if (servoRead - 3 > 0 and servoRead <= 180) {
                   servo.write (int(servoRead) - 3); 
                   writePosServo(int(servoRead) - 3, numServo);
                   //delay(25);
               }
            }
} 
void serialRead() {
    while(Serial.available()>0) {
         Serial.readBytes(msgByte, sizeof(msgByte)); 
         if (msgByte[0] == 1) {          //byte id servo
            servoPosition (servo1, msgByte[1], 1);
         } else if (msgByte[0] == 2) {
            servoPosition (servo2, msgByte[1], 2);
         } else if (msgByte[0] == 3) {
            servoPosition (servo3, msgByte[1], 3);
         } else if (msgByte[0] == 4) {
            servoPosition (servo4, msgByte[1], 4);
            //servo4.write (angle(int(msgByte[1])));     
         } else if (msgByte[0] == 9 and msgByte[1] == 1 and msgByte[2] == 1 and msgByte[3] == 0 and msgByte[4] == 3 and msgByte[5] == 1) {
            Serial.print("Hi! Im Pedro");
         }

         if (msgByte[0] == 99) { 
            if (msgByte[1] == 44) {          //record
               if (inRecord == false) {
                   inRecord = true;
                   record();
               }
            } else if (msgByte[1] == 55) {   //play
                addr = 0;
                digitalWrite (10, HIGH); //rouge
                replaying = true;
                replay();
            } else if (msgByte[1] == 66) {   //pause
               btnStop = true;
            } else if (msgByte[1] == 77) {   //stop
               serialStop = true;
            } else if (msgByte[1] == 88) {   //clear
               btnStop = true;
            } else if (msgByte[1] == 99) {   //speed
               btnStop = true;
            }

         }
    }
}
int angle(int valeur_angle) { 
        int impuls=0;
        impuls=map(valeur_angle,ANGLE_MIN,ANGLE_MAX,POS_MIN, POS_MAX);
        return impuls;   
}
