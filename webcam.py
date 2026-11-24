import cv2
import serial
import time
import numpy as np


# إعدادات الاتصال والكاميرا

SERIAL_PORT = 'COM9'
BAUD_RATE = 9600
MAX_ATTEMPTS = 4          # عدد المحاولات لكل شخص

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)
    print(f"Connected to Arduino on port: {SERIAL_PORT}")
except Exception as e:
    print(f"Error connecting to Arduino: {e}")
    exit()

camera_index = 1
cap = cv2.VideoCapture(camera_index)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)   # عرض
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)   # ارتفاع

if not cap.isOpened():
    print("ERROR: camera not recognized")
    exit()

# إعدادات الكاميرا أوتوماتيك (معلّقة)
# cap.set(cv2.CAP_PROP_AUTO_WB, 0)
# cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)

score = 0
attempts = MAX_ATTEMPTS   # المحاولات المتبقية
last_color_text = "Ready!"
text_color = (255, 255, 255)


# حدود الألوان (H) وحدود التشبّع (S) لكل لون

BLUE_RANGE   = (100, 135)
PURPLE_RANGE = (136, 179)
YELLOW_RANGE = (8, 38)
GREEN_RANGE  = (39, 99)     # عدّلناه (كان 39 إلى 85)

YELLOW_MIN_SAT = 18
PURPLE_MIN_SAT = 25
BLUE_MIN_SAT   = 40
GREEN_MIN_SAT  = 20         # عدّلناه (كان 40)

MIN_VAL = 40              # أقل سطوع (أقل منه أسود)
WHITE_SAT = 18            # أقل منه أبيض/رمادي


# ألوان النص على شاشة اللابتوب

color_bgr = {
    "YELLOW / ORANGE": (0, 165, 255),
    "GREEN": (0, 255, 0),
    "BLUE": (255, 0, 0),
    "PURPLE": (255, 0, 255),
}


# دوال الإرسال وتحليل الألوان

def send_update():
    ser.write(f"UPDATE:{attempts}:{score}:{last_color_text}\n".encode('utf-8'))

def classify(h, s, v):
    if v < MIN_VAL:
        return None, 0, "NO COLOR"
    if YELLOW_RANGE[0] <= h <= YELLOW_RANGE[1] and s >= YELLOW_MIN_SAT:
        return "YELLOW / ORANGE", 6, None
    if GREEN_RANGE[0] <= h <= GREEN_RANGE[1] and s >= GREEN_MIN_SAT:
        return "GREEN", 2, None
    if BLUE_RANGE[0] <= h <= BLUE_RANGE[1] and s >= BLUE_MIN_SAT:
        return "BLUE", 4, None
    if PURPLE_RANGE[0] <= h <= PURPLE_RANGE[1] and s >= PURPLE_MIN_SAT:
        return "PURPLE", 8, None
    if s < WHITE_SAT:
        return None, 0, "NO COLOR"
    return None, 0, "WRONG"

def detect_color_and_score(clean_frame):
    global score, attempts, last_color_text, text_color

    # كل ضغطة = محاولة وحدة بتنخصم، سواء أصاب أو أخطأ
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
    print(f"H:{h:.1f}, S:{s:.1f}, V:{v:.1f}")

    color, points, fail = classify(h, s, v)

    if color is None:
        last_color_text = f"{fail} (+0)"
        text_color = (0, 0, 255)
        print(fail)
        send_update()
        return

    score += points
    last_color_text = f"{color} (+{points})"
    text_color = color_bgr.get(color, (255, 255, 255))
    print(color)
    send_update()


# الحلقة الرئيسية

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        clean_frame = frame.copy()   # نسخة نظيفة للتحليل (بدون رسم)

        height, width, _ = frame.shape
        cx, cy = width // 2, height // 2

        # مربع التصويب (نفس حجم منطقة القراءة)
        box_size = 20
        cv2.rectangle(frame, (cx - box_size, cy - box_size),
                      (cx + box_size, cy + box_size), (0, 255, 255), 2)
        cv2.circle(frame, (cx, cy), 3, (0, 0, 255), -1)

        # النقاط
        cv2.putText(frame, f"Score: {score}", (30, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 3)

        # المحاولات (4 دوائر)
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

        # بعد Game Over بيرجع تلقائياً للشخص اللي بعده
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
    print("\nThe game is paused!")

finally:
    cap.release()
    ser.close()
    cv2.destroyAllWindows()