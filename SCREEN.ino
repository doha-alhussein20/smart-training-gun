#include <Wire.h>
#include <Adafruit_GFX.h>//حجم الخط تدوير الشاشة ورسم الأشكال:مكتبة الرسوميات
#include <Adafruit_SSD1306.h>//التحكم بنوع الشاشة

#define SCREEN_WIDTH 128 // Xعرض الشاشة 
#define SCREEN_HEIGHT 64 // Yارتفاع الشاشة

// إنشاء كائن الشاشة
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);//-1 مصممة لتدعم الشاشات التي تحتوي دبوس خامس

void setup() {
  // تشغيل الشاشة على العنوان الافتراضي 0x3C
  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) { //إذا ما لقينا الشاشة بهاد العنوان بنوقف البرنامج
    for(;;); // التوقف هنا إذا لم تفتح الشاشة
  }

  display.clearDisplay(); // مسح الذاكرة المؤقتة للشاشة

  display.setTextSize(2);              // ضبط حجم الخط إلى أصغر مقاس (1)
  display.setTextColor(SSD1306_WHITE);
    // تحديد لون النص (أبيض)
   
  display.setCursor(1, 1);             // بدء الكتابة من أعلى الزاوية اليسرى (X=0, Y=0)
  
  display.println("Hello World!");     // النص المراد طباعته
  
  display.display(); // هذا الأمر ضروري جداً لإظهار النص على الشاشة
}

void loop() {
  // ترك الدالة فارغة لأننا نريد طباعة النص مرة واحدة فقط في الـ setup
}