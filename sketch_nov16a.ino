#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <SoftwareSerial.h>
#include <DFRobotDFPlayerMini.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
#define MAX_ATTEMPTS 4

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

SoftwareSerial mySoftwareSerial(10, 11);
DFRobotDFPlayerMini myDFPlayer;

const int buttonPin = 5;
const int laserPin = 3;

int lastButtonState = LOW;          // INPUT_PULLDOWEN: 
int currentAttempts = MAX_ATTEMPTS;  // المحاولات المتبقية
int currentScore = 0;
String lastMessage = "Ready!";

// منع ضغطة ثانية قبل ما يوصل رد البايثون
bool waitingResult = false;
unsigned long captureTime = 0;

//  oledمصفوفة لرسم القلوب على ال 
const unsigned char PROGMEM heart_bmp[] = {
  0b00000000, 0b00000000,
  0b01100110, 0b00000000,
  0b11111111, 0b10000000,
  0b11111111, 0b10000000,
  0b11111111, 0b10000000,
  0b01111111, 0b00000000,
  0b00111110, 0b00000000,
  0b00011100, 0b00000000,
  0b00001000, 0b00000000
};

void setup() {
  Serial.begin(9600);
  mySoftwareSerial.begin(9600);

  pinMode(buttonPin, INPUT_PULLUP);
  pinMode(laserPin, OUTPUT);
  digitalWrite(laserPin, LOW);

  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    for (;;);
  }
  display.setTextColor(SSD1306_WHITE);//حددنا الون هون منشان ما ضل كل ما بدي أكتب على الشاشة حدد اللون

  if (myDFPlayer.begin(mySoftwareSerial)) {
    myDFPlayer.volume(5);
  }

  updateOLEDDisplay();
}

void loop() {
  // تحرير القفل إذا ما وصل رد خلال ثانيتين
  if (waitingResult && millis() - captureTime > 2000) {
    waitingResult = false;
  }

  // إذا ضغط على الزر
  int reading = digitalRead(buttonPin);
  if (currentAttempts > 0 && !waitingResult &&
      reading == HIGH && lastButtonState == LOW) {
    Serial.println("CAPTURE");//هون بيرسل للكود البايثون كلمة capture
    waitingResult = true;
    captureTime = millis();

    digitalWrite(laserPin, HIGH);//هون بيشتغل الليزر
    myDFPlayer.play(1);//هون بيشتغل الصوت
    delay(500);
    digitalWrite(laserPin, LOW);

    delay(200);
  }
  lastButtonState = reading;

  //  استقبال البيانات من البايثون
  if (Serial.available() > 0) {
    String incoming = Serial.readStringUntil('\n');
    incoming.trim();

    if (incoming == "RESET") {
      currentAttempts = MAX_ATTEMPTS;
      currentScore = 0;
      lastMessage = "Restarted!";
      waitingResult = false;
      updateOLEDDisplay();
    }
    else if (incoming.startsWith("UPDATE:")) {
      // الصيغة: UPDATE:attempts:score:message
      int firstColon = incoming.indexOf(':');
      int secondColon = incoming.indexOf(':', firstColon + 1);
      int thirdColon = incoming.indexOf(':', secondColon + 1);

      if (secondColon != -1) {
        currentAttempts = incoming.substring(firstColon + 1, secondColon).toInt();

        if (thirdColon != -1) {
          currentScore = incoming.substring(secondColon + 1, thirdColon).toInt();
          lastMessage = incoming.substring(thirdColon + 1);
        } else {
          currentScore = incoming.substring(secondColon + 1).toInt();
        }
        waitingResult = false;
        updateOLEDDisplay();
      }
    }
  }
}

void updateOLEDDisplay() {
  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);

  if (currentAttempts <= 0) {
    // GAME OVER مع النقاط النهائية
    display.setTextSize(2);
    display.setCursor(4, 12);
    display.println(F("GAME OVER!"));

    display.setTextSize(1);
    display.setCursor(20, 42);
    display.print(F("FINAL SCORE: "));
    display.print(currentScore);
  } else {
    display.setTextSize(1);
    display.setCursor(0, 0);
    display.print(F("SCORE: "));

    display.setTextSize(2);
    display.setCursor(40, 0);
    display.print(currentScore);

    display.drawLine(0, 18, 128, 18, SSD1306_WHITE);//نرسم خط

    display.setTextSize(1);
    display.setCursor(0, 22);
    display.print(lastMessage);

    display.drawLine(0, 34, 128, 34, SSD1306_WHITE);//نرسم خط

    display.setCursor(0, 45);
    display.print(F("TRIES:"));
//قلب وجود معناتو فيه محاولة صار مربع راحت محاولة
    int xPos = 42;
    for (int i = 0; i < MAX_ATTEMPTS; i++) {
      if (i < currentAttempts) {
        display.drawBitmap(xPos + (i * 20), 43, heart_bmp, 12, 9, SSD1306_WHITE);
      } else {
        display.drawRect(xPos + (i * 20), 43, 12, 9, SSD1306_WHITE);
      }
    }
  }

  display.display();
}