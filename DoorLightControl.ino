String command;
int state = 1;
int sent_again = 0;
int waiting_period = 3;
int sent_counter = 0;
int counter = 0;


#define Light 8
#define Door 9

void setup() {
  Serial.begin(9600);
  pinMode(Light, OUTPUT);
  pinMode(Door, OUTPUT);
}

void loop() {
  if (Serial.available()) {
    command = Serial.readStringUntil('\n');
    command.trim();
    if (command.equals("light0")) {
      Serial.println("light"); 
      digitalWrite(Light, LOW);
    }
    else if (command.equals("light1")) {
      Serial.println("light"); 
      digitalWrite(Light, HIGH);
    }
    else if(command.equals("door1")){
      Serial.println("door"); 
      digitalWrite(Door, HIGH);
    }else if(command.equals("door0")){
      Serial.println("door"); 
      digitalWrite(Door, LOW);
    }
 }
 delay(10);
}
