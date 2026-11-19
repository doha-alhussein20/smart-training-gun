import cv2
import serial
import time
import numpy as np
#  إعدادات الاتصال والكاميرا

SERIAL_PORT = 'COM9'
BAUD_RATE = 9600
MAX_ATTEMPTS = 4          # عدد المحاولات لكل شخص

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)
    print(f" Connected to Arduino on port: {SERIAL_PORT}")
except Exception as e:
    print(f" Error connecting to Arduino: {e}")
    exit()

camera_index = 1
cap = cv2.VideoCapture(camera_index)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

if not cap.isOpened():
    print(" ERROR:camera not recognized")
    exit()

cap.set(cv2.CAP_PROP_AUTO_WB, 0)
cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)

score = 0
attempts = MAX_ATTEMPTS   # المحاولات المتبقية
last_color_text = "Ready!"
text_color = (255, 255, 255)
# ألوان النص على شاشة اللابتوب

color_bgr = {
    "YELLOW / ORANGE": (0, 165, 255),
    "GREEN": (0, 255, 0),
    "BLUE": (255, 0, 0),
    "PURPLE": (255, 0, 255),
}
#  دوال الإرسال وتحليل الألوان

def send_update():
    ser.write(f"UPDATE:{attempts}:{score}:{last_color_text}\n".encode('utf-8'))

def detect_color_and_score(clean_frame):
    global score, attempts, last_color_text, text_color

    # كل ما يضغط مرة وحدة بيروح منو قلب  سواء أطلق صح أو غلط
    attempts = max(0, attempts - 1)

    height, width, _ = clean_frame.shape
    cx, cy = width // 2, height // 2
    crop_size = 20

    roi = clean_frame[cy - crop_size: cy + crop_size,
                      cx - crop_size: cx + crop_size]

    hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    h = float(np.median(hsv_roi[:, :, 0]))
    s = float(np.median(hsv_roi[:, :, 1]))
    v = float(np.median(hsv_roi[:, :, 2]))

    print(f"📊 H:{h:.1f}, S:{s:.1f}, V:{v:.1f}")

    if v < 40:
        last_color_text = "NO COLOR (+0)"
        text_color = (0, 0, 255)
        print(" NO COLOR")
        send_update()
        return

    # الأصفر / البرتقالي
    if 8 <= h <= 38 and s >= 40:
        detected_color, points = "YELLOW / ORANGE", 6
    # البنفسجي
    elif 126 <= h <= 175 and s >= 45:
        detected_color, points = "PURPLE", 8
    
    elif s < 70:
        last_color_text = "NO COLOR (+0)"
        text_color = (0, 0, 255)
        print(" NO COLOR")
        send_update()
        return
    #الأخضر
    elif 39 <= h <= 85:
        detected_color, points = "GREEN", 2
    #الأزرق
    elif 86 <= h <= 125:
        detected_color, points = "BLUE", 4

    else:
        last_color_text = "WRONG (+0)"
        text_color = (0, 0, 255)
        print(" WRONG")
        send_update()
        return

    # إصابة صح
    score += points
    last_color_text = f"{detected_color} (+{points})"
    text_color = color_bgr.get(detected_color, (255, 255, 255))
    print(f" {detected_color}")
    send_update()


#  الحلقة الرئيسية

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        clean_frame = frame.copy()

        height, width, _ = frame.shape
        cx, cy = width // 2, height // 2

        # مربع التصويب
        box_size = 15
        
        cv2.rectangle(frame, (cx - box_size, cy - box_size),
                      (cx + box_size, cy + box_size), (0, 255, 255), 2)
        cv2.circle(frame, (cx, cy), 3, (0, 0, 255), -1)

        # النقاط
        cv2.putText(frame, f"Score: {score}", (30, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 3)

        # المحاولات كقلوب (4 قلوب)
        cv2.putText(frame, "Tries:", (30, 110),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
        for i in range(MAX_ATTEMPTS):
            pos = (200 + i * 45, 98)
            if i < attempts:
                cv2.circle(frame, pos, 15, (0, 0, 255), -1)
            else:
                cv2.circle(frame, pos, 15, (0, 0, 255), 2)

        cv2.putText(frame, f"Result: {last_color_text}", (30, 170),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, text_color, 2)

#بعد ما يطلع game over بيرجع تلقائيا للدور اللي بعدو
        if attempts <= 0:
            cv2.putText(frame, f"GAME OVER! Final score: {score}",
                        (width // 8, height // 2),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 255), 3)
            cv2.imshow("Color Game System", frame)
            cv2.waitKey(5000)

            score = 0
            attempts = MAX_ATTEMPTS
            last_color_text = "Restarted!"
            text_color = (255, 255, 255)
            ser.write(b"RESET\n")
            ser.reset_input_buffer()
            continue

        cv2.imshow("Color Game System", frame)

        # الاستماع لإشارة الزر من الأردوينو
        if ser.in_waiting > 0:
            try:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if "CAPTURE" in line and attempts > 0:
                    detect_color_and_score(clean_frame)
            except Exception:
                pass

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("\n the game is paused!")

finally:
    cap.release()
    ser.close()
    cv2.destroyAllWindows()