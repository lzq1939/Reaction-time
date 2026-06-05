// Define LED and button pins
const int LEDPin1 = 2;  // LED1 pin
const int LEDPin2 = 3;  // LED2 pin
const int LEDPin3 = 5;  // LED3 pin
const int LEDPin4 = 6;  // LED4 pin
const int buttonYes = 57; // "Yes" button pin
const int buttonNo = 56;  // "No" button pin

int startTime;    // Record the start time when LED lights up
int reactionTime; // Record the reaction time
int activeLEDOld = -1;

// Define target LEDs
const int targetLEDs[2] = {LEDPin1, LEDPin2}; 

void setup() {
  pinMode(LEDPin1, OUTPUT);
  pinMode(LEDPin2, OUTPUT);
  pinMode(LEDPin3, OUTPUT);
  pinMode(LEDPin4, OUTPUT);

  pinMode(buttonYes, INPUT_PULLUP);
  pinMode(buttonNo,  INPUT_PULLUP);

  Serial.begin(115200);
  randomSeed(analogRead(0));

  Serial.println("Begin!");
  delay(3000); // Wait for 3 seconds
}

void loop() {
  // Randomly select an LED
  int arr[4] = {2, 3, 5, 6};
  int activeLED;

  if(activeLEDOld < 0) {
    activeLED = arr[random(0, 4)];
  } else {
    do {
      activeLED = arr[random(0, 4)];
    } while(activeLED == activeLEDOld);
  }
  activeLEDOld = activeLED;

  // Turn off all LEDs
  digitalWrite(LEDPin1, LOW);
  digitalWrite(LEDPin2, LOW);
  digitalWrite(LEDPin3, LOW);
  digitalWrite(LEDPin4, LOW);

  digitalWrite(activeLED, HIGH); // Turn on the selected LED
  
  // Record the light-up time
  startTime = millis();


  while (true) {
    if (digitalRead(buttonYes) == HIGH || digitalRead(buttonNo) == HIGH) {
      reactionTime = millis() - startTime; // Calculate the reaction time

      bool isTarget = (activeLED == targetLEDs[0] || activeLED == targetLEDs[1]); 
     
      // Column 1: Yes/No
      // Column 2: reactionTime
      // Column 3: startTime
      if ((isTarget && digitalRead(buttonYes) == HIGH) || (!isTarget && digitalRead(buttonNo) == HIGH)) {
       
        Serial.print("Yes");         // Column 1
        Serial.print(",");           // Separate with comma
        Serial.print(reactionTime);  // Column 2
        Serial.print(",");
        Serial.println(startTime);   // Column 3 
      } else {
        
        Serial.print("No");          // Column 1
        Serial.print(",");
        Serial.print(reactionTime);  // Column 2
        Serial.print(",");
        Serial.println(startTime);   // Column 3 
      }
      
      break; 
    }
  }

  // Wait for one second to prevent repeated triggers
  delay(1000);
}
