const int greenPins[]  = {A7, 3, A4, 50, 23, 7, 8, 26};
const int bluePins[]   = {22, 5, 24, 51, 52, 4};
const int yellowPins[] = {6, 27, 25, A5, A6, 2,53};

// ضبط العدد الفعلي للعناصر لتجنب القراءة خارج المصفوفة
const int totalGreen  = sizeof(greenPins)  / sizeof(greenPins[0]);
const int totalBlue   = sizeof(bluePins)   / sizeof(bluePins[0]);
const int totalYellow = sizeof(yellowPins) / sizeof(yellowPins[0]);

// أطراف الـ RGB البنفسجي
const int redPin  = 31;
const int bluePin = 47;



int greenOrder[8];
int blueOrder[6];
int yellowOrder[6];
int stepIndex = 0;

void setup() {
  for (int i = 0; i < totalGreen; i++) {
    pinMode(greenPins[i], OUTPUT);
    digitalWrite(greenPins[i], LOW);
    greenOrder[i] = i;
  }
  for (int i = 0; i < totalBlue; i++) {
    pinMode(bluePins[i], OUTPUT);
    digitalWrite(bluePins[i], LOW);
    blueOrder[i] = i;
  }
  for (int i = 0; i < totalYellow; i++) {
    pinMode(yellowPins[i], OUTPUT);
    digitalWrite(yellowPins[i], LOW);
    yellowOrder[i] = i;
  }

  pinMode(redPin, OUTPUT);
  pinMode(bluePin, OUTPUT);

  turnOffAllLeds();

  randomSeed(analogRead(A0));

  shuffleArray(greenOrder, totalGreen);
  shuffleArray(blueOrder, totalBlue);
  shuffleArray(yellowOrder, totalYellow);
}

void loop() {
  int gIdx = greenOrder[stepIndex % totalGreen];
  int bIdx = blueOrder[stepIndex % totalBlue];
  int yIdx = yellowOrder[stepIndex % totalYellow];

  //  تشغيل ليد خضراء ثم إطفائها
  turnOffAllLeds();
  digitalWrite(greenPins[gIdx], HIGH);
  delay(5000);
  turnOffAllLeds();
    

  //  تشغيل ليد زرقاء ثم إطفائها
  turnOffAllLeds();
  digitalWrite(bluePins[bIdx], HIGH);
  delay(5000);
  turnOffAllLeds();
 

  // تشغيل ليد صفراء ثم إطفائها
  turnOffAllLeds();
  digitalWrite(yellowPins[yIdx], HIGH);
  delay(5000);
  turnOffAllLeds();

  // تشغيل البنفسجي ثم إطفائه
  turnOffAllLeds();
  digitalWrite(redPin, LOW);
  digitalWrite(bluePin, LOW);
  delay(5000);
  digitalWrite(redPin, HIGH);
  digitalWrite(bluePin, HIGH);
  delay(5000 );

  stepIndex++;

  if (stepIndex >= totalGreen) {
    stepIndex = 0;
    shuffleArray(greenOrder, totalGreen);
    shuffleArray(blueOrder, totalBlue);
    shuffleArray(yellowOrder, totalYellow);
  }
}

void shuffleArray(int arr[], int size) {
  for (int i = size - 1; i > 0; i--) {
    int j = random(0, i + 1);
    int temp = arr[i];
    arr[i] = arr[j];
    arr[j] = temp;
  }
}

void turnOffAllLeds() {
  for (int i = 0; i < totalGreen; i++) digitalWrite(greenPins[i], LOW);
  for (int i = 0; i < totalBlue; i++) digitalWrite(bluePins[i], LOW);
  for (int i = 0; i < totalYellow; i++) digitalWrite(yellowPins[i], LOW);

  digitalWrite(redPin, HIGH);
  digitalWrite(bluePin, HIGH);
}