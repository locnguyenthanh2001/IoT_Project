#include "HUSKYLENS.h"
#include "SoftwareSerial.h"
#include "MQ135.h"

MQ135 gasSensor = MQ135(A0);

int husky_state = 0;
int counter_husky = 0;
int state = 0;
int counter = 0;

int sensor  = A0;
int lamp = 8;
int senvalue = 0;

HUSKYLENS huskylens;
SoftwareSerial mySerial(10, 11); // RX, TX
//HUSKYLENS green line >> Pin 10; blue line >> Pin 11
void printResult(HUSKYLENSResult result);

void setup() {
  pinMode(lamp, OUTPUT);
  Serial.begin(9600);
  mySerial.begin(9600);
  while (!huskylens.begin(mySerial))
  {
    Serial.println(F("Begin failed!"));
    Serial.println(F("1.Please recheck the \"Protocol Type\" in HUSKYLENS (General Settings>>Protocol Type>>Serial 9600)"));
    Serial.println(F("2.Please recheck the connection."));
    delay(100);
  }
}

void loop() {
  if (state == 0) {
    senvalue = analogRead(sensor);
    state = 1;
  } else if (state == 1) {
    if (senvalue < 800) {
      Serial.println("lamp1");
      digitalWrite(lamp, HIGH);
    }
    else {
      Serial.println("lamp0");
      digitalWrite(lamp, LOW);
    }
    state = 2;
  }else{
    if(counter < 1300) counter++;
    else{
      counter = 0;
      state = 0;
    }
  }
  if (husky_state == 0) {
    if (!huskylens.request()) Serial.println(F("Fail to request data from HUSKYLENS, recheck the connection!"));
    else husky_state = 1;

  } else if (husky_state == 1) {
    if (!huskylens.available()) {
      Serial.println("camera99");
      husky_state = 2;
    } else {
      HUSKYLENSResult result = huskylens.read();
      printResult(result);
      husky_state = 2;
    }
  } else if (husky_state == 2) {
    if (counter_husky < 600) counter_husky++;
    else {
      husky_state = 0;
      counter_husky = 0;
    }
  }
  delay(10);
}

void printResult(HUSKYLENSResult result) {
  if (result.command == COMMAND_RETURN_BLOCK) {
    Serial.println(String() + F("camera") + result.ID);
  }
}
