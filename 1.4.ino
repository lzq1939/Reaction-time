// LED pins
const int LEDPin1 = 2;
const int LEDPin2 = 3;
const int LEDPin3 = 5;
const int LEDPin4 = 6;
const int LEDPin_start = 4;

// sensor pins
const int ForceSensor1 = 57;
const int ForceSensor2 = 56;
const int ForceSensor3 = 55;
const int ForceSensor4 = 54;

const double t_step = 12000;  // total number of loops
const int t_reso = 5;         // time resolution (ms)

String spacer = ", ";  // separator used in the output file

const int nRounds = 5;  
int round_length = t_step / nRounds;  

double i = 0;  // used for counting loop number

// time status
int experiment_start_time;  // experiment start time (millis)
double current_time;        // time (relative to experiment_start_time)

// sensor readings
int sensorReading1;
int sensorReading2;
int sensorReading3;
int sensorReading4;

// array to store LED status readings (1=Off, 0=On)
int LED1;
int LED2;
int LED3;
int LED4;

// Shuffle function
void shuffleArray(int arr[], int n) {
  for (int k = n - 1; k > 0; k--) {
    int j = random(0, n);
    // swap arr[k] and arr[j]
    int temp = arr[k];
    arr[k] = arr[j];
    arr[j] = temp;
  }
}

void setup() {
  pinMode(LEDPin1, OUTPUT);
  pinMode(LEDPin2, OUTPUT);
  pinMode(LEDPin3, OUTPUT);
  pinMode(LEDPin4, OUTPUT);
  pinMode(LEDPin_start, OUTPUT);

  Serial.begin(115200);
}

void loop() {
  if (i == 0)  // condition to stop the loop after completing one cycle
  {
    // Use the analog pin to generate a random seed so each power-on has a different random sequence
    randomSeed(analogRead(0));

    // Print the header
    Serial.print("time(ms)");
    Serial.print(spacer);
    Serial.print("sensor#1");
    Serial.print(spacer);
    Serial.print("sensor#2");
    Serial.print(spacer);
    Serial.print("sensor#3");
    Serial.print(spacer);
    Serial.print("sensor#4");
    Serial.print(spacer);
    Serial.print("LED1");
    Serial.print(spacer);
    Serial.print("LED2");
    Serial.print(spacer);
    Serial.print("LED3");
    Serial.print(spacer);
    Serial.println("LED4");

    // First, turn off all LEDs
    digitalWrite(LEDPin1, LOW);
    digitalWrite(LEDPin2, LOW);
    digitalWrite(LEDPin3, LOW);
    digitalWrite(LEDPin4, LOW);
    digitalWrite(LEDPin_start, LOW);

    // Short delay to give preparation time
    delay(3000);

    // Turn on the start indicator LED
    digitalWrite(LEDPin_start, HIGH);
    experiment_start_time = millis();  // Record the starting time

    // Run through nRounds
    for (int roundIndex = 0; roundIndex < nRounds; roundIndex++) {
      // Prepare an array with 16 elements (each LED pin repeated 4 times) 
      int ledPins16[16] = {
        LEDPin1, LEDPin1, LEDPin1, LEDPin1,
        LEDPin2, LEDPin2, LEDPin2, LEDPin2,
        LEDPin3, LEDPin3, LEDPin3, LEDPin3,
        LEDPin4, LEDPin4, LEDPin4, LEDPin4
      };

      // Shuffle the array randomly 
      shuffleArray(ledPins16, 16);


      int sub_length = round_length / 16;

      // Activate LEDs according to the shuffled order
      for (int sub = 0; sub < 16; sub++) {
        // If i exceeds t_step, exit the experiment
        if (i >= t_step) {
          goto END_EXPERIMENT;
        }

        int currentLedPin = ledPins16[sub];

        // Keep current LED on for sub_length steps, others off
        for (int stepInSub = 0; stepInSub < sub_length; stepInSub++) {
          i += 1;
          if (i > t_step) {
          
            goto END_EXPERIMENT;
          }

          // Control which LED is on
          digitalWrite(LEDPin1, (currentLedPin == LEDPin1) ? HIGH : LOW);
          digitalWrite(LEDPin2, (currentLedPin == LEDPin2) ? HIGH : LOW);
          digitalWrite(LEDPin3, (currentLedPin == LEDPin3) ? HIGH : LOW);
          digitalWrite(LEDPin4, (currentLedPin == LEDPin4) ? HIGH : LOW);

          // Read sensor values
          sensorReading1 = analogRead(ForceSensor1);
          sensorReading2 = analogRead(ForceSensor2);
          sensorReading3 = analogRead(ForceSensor3);
          sensorReading4 = analogRead(ForceSensor4);

          // Set LED status (1=Off, 0=On)
          LED1 = (digitalRead(LEDPin1) ^ 1);
          LED2 = (digitalRead(LEDPin2) ^ 1);
          LED3 = (digitalRead(LEDPin3) ^ 1);
          LED4 = (digitalRead(LEDPin4) ^ 1);

          current_time = millis() - experiment_start_time;

          // Serial output
          String sensor_out = String(current_time) + spacer
                              + String(sensorReading1) + spacer
                              + String(sensorReading2) + spacer
                              + String(sensorReading3) + spacer
                              + String(sensorReading4) + spacer
                              + String(LED1) + spacer
                              + String(LED2) + spacer
                              + String(LED3) + spacer
                              + String(LED4);
          Serial.println(sensor_out);

          delay(t_reso);  // Wait for t_reso ms
        }
      }
    }
  }

END_EXPERIMENT:

  // Turn off all LEDs
  digitalWrite(LEDPin1, LOW);
  digitalWrite(LEDPin2, LOW);
  digitalWrite(LEDPin3, LOW);
  digitalWrite(LEDPin4, LOW);
  digitalWrite(LEDPin_start, LOW);

  
  while (true) {
    // Remove this while(true) if you want the experiment to loop
  }
}
