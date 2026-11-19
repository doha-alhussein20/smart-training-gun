#include <SoftwareSerial.h>
#include <DFRobotDFPlayerMini.h>

SoftwareSerial mySoftwareSerial(10, 11); // RX, TX
DFRobotDFPlayerMini myDFPlayer;

void setup() {
  pinMode(7,INPUT);
  Serial.begin(115200);
  mySoftwareSerial.begin(9600);

  Serial.println("Initializing DFPlayer...");

  if (!myDFPlayer.begin(mySoftwareSerial)) {
    Serial.println("DFPlayer connection failed!");
    while (true);
  }

  Serial.println("DFPlayer connected!");

  myDFPlayer.volume(3);  // مستوى الصوت من 0 إلى 30
  delay(200);

  Serial.print("Files on SD card: ");
Serial.print("SD card state: ");
Serial.println(myDFPlayer.readState());

Serial.print("Files in SD: ");
Serial.println(myDFPlayer.readFileCounts());

Serial.print("Files in SD root: ");
Serial.println(myDFPlayer.readFileCountsInFolder(0));
  myDFPlayer.play(1);
    // تشغيل الملف الأول
//هون وقت بيطلع صوت 

     delay(200);
       myDFPlayer.play(1);
  Serial.println("Play command sent!");

}

void loop() {
  if (myDFPlayer.available()) {
    Serial.print("DFPlayer message: ");
    Serial.println(myDFPlayer.readType());
  }
}