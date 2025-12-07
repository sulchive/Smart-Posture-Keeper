import sys
import cv2
import mediapipe as mp
import numpy as np
import time
import os
import platform
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSlider, QFrame, QMessageBox
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap, QIcon

# --- [1] 자세 모니터링 클래스 ---
class PostureMonitor:
    def __init__(self):
        self.mp_holistic = mp.solutions.holistic
        self.mp_drawing = mp.solutions.drawing_utils
        self.holistic = self.mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        
        self.LEFT_EYE_IDX = [33, 160, 158, 133, 153, 144]
        self.RIGHT_EYE_IDX = [362, 385, 387, 263, 373, 380]
        
        self.warning_duration = 0
        self.neck_threshold = 0.28 # 거북목 민감도 기본값 (조절 가능)
        
        # 통계 변수
        self.total_frames = 0
        self.bad_posture_frames = 0

    def calculate_ear(self, landmarks, indices):
        p2_p6 = np.linalg.norm(np.array(landmarks[indices[1]]) - np.array(landmarks[indices[5]]))
        p3_p5 = np.linalg.norm(np.array(landmarks[indices[2]]) - np.array(landmarks[indices[4]]))
        p1_p4 = np.linalg.norm(np.array(landmarks[indices[0]]) - np.array(landmarks[indices[3]]))
        return (p2_p6 + p3_p5) / (2.0 * p1_p4)

    def process_frame(self, frame):
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = self.holistic.process(image)
        image.flags.writeable = True
        
        height, width, _ = image.shape
        status = "Good"
        color = (0, 255, 0)
        
        if results.face_landmarks and results.pose_landmarks:
            # 통계 집계
            self.total_frames += 1

            # 1. 졸음 감지
            face_landmarks = results.face_landmarks.landmark
            coords = [(p.x * width, p.y * height) for p in face_landmarks]
            left_ear = self.calculate_ear(coords, self.LEFT_EYE_IDX)
            right_ear = self.calculate_ear(coords, self.RIGHT_EYE_IDX)
            
            if (left_ear + right_ear) / 2.0 < 0.20:
                status = "WAKE UP!"
                color = (255, 0, 0)

            # 2. 거북목 감지
            pose_landmarks = results.pose_landmarks.landmark
            ear_y = pose_landmarks[self.mp_holistic.PoseLandmark.LEFT_EAR].y
            shoulder_y = pose_landmarks[self.mp_holistic.PoseLandmark.LEFT_SHOULDER].y
            
            diff = shoulder_y - ear_y
            
            if diff < self.neck_threshold:
                if status == "Good": # 졸음이 아닐 때만 거북목 표시
                    status = "Turtle Neck!"
                    color = (255, 0, 0)
                self.bad_posture_frames += 1 # 나쁜 자세 카운트

            # 그리기
            self.mp_drawing.draw_landmarks(image, results.face_landmarks, self.mp_holistic.FACEMESH_TESSELATION, 
                                           None, mp.solutions.drawing_styles.get_default_face_mesh_tesselation_style())
            self.mp_drawing.draw_landmarks(image, results.pose_landmarks, self.mp_holistic.POSE_CONNECTIONS, 
                                           mp.solutions.drawing_styles.get_default_pose_landmarks_style())

        return image, status, color

# --- [2] 메인 윈도우 클래스 ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smart Posture Keeper (거북목 지킴이)")
        self.setGeometry(100, 100, 1000, 700)
        self.setStyleSheet("background-color: #2b2b2b; color: white;")

        self.monitor = PostureMonitor()
        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.is_running = False
        self.initUI()

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        self.video_label = QLabel("Camera OFF")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("background-color: black; border: 2px solid #555;")
        self.video_label.setFixedSize(640, 480)
        main_layout.addWidget(self.video_label)

        control_panel = QFrame()
        control_panel.setStyleSheet("background-color: #3d3d3d; border-radius: 10px;")
        control_layout = QVBoxLayout(control_panel)
        
        title_label = QLabel("🔍 AI 감시 제어판")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #00e5ff;")
        control_layout.addWidget(title_label)
        
        control_layout.addStretch(1)

        self.status_label = QLabel("상태: 대기중")
        self.status_label.setStyleSheet("font-size: 24px; font-weight: bold; color: yellow;")
        self.status_label.setAlignment(Qt.AlignCenter)
        control_layout.addWidget(self.status_label)

        control_layout.addStretch(1)

        control_layout.addWidget(QLabel("거북목 민감도 조절"))
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(5)
        self.slider.setMaximum(50)
        self.slider.setValue(int(self.monitor.neck_threshold * 100))
        self.slider.valueChanged.connect(self.update_threshold)
        control_layout.addWidget(self.slider)
        
        self.threshold_value_label = QLabel(f"현재 기준값: {self.monitor.neck_threshold}")
        self.threshold_value_label.setAlignment(Qt.AlignCenter)
        control_layout.addWidget(self.threshold_value_label)

        control_layout.addStretch(1)

        self.btn_start = QPushButton("🚀 감시 시작")
        self.btn_start.setStyleSheet("background-color: #00c853; color: white; font-size: 18px; padding: 15px; border-radius: 8px;")
        self.btn_start.clicked.connect(self.toggle_monitoring)
        control_layout.addWidget(self.btn_start)

        main_layout.addWidget(control_panel)

    def update_threshold(self):
        val = self.slider.value() / 100.0
        self.monitor.neck_threshold = val
        self.threshold_value_label.setText(f"현재 기준값: {val}")

    def toggle_monitoring(self):
        if not self.is_running:
            self.cap = cv2.VideoCapture(0)
            self.timer.start(30)
            self.btn_start.setText("🛑 감시 종료")
            self.btn_start.setStyleSheet("background-color: #ff3d00; color: white; font-size: 18px; padding: 15px; border-radius: 8px;")
            self.is_running = True
        else:
            self.timer.stop()
            if self.cap: self.cap.release()
            self.video_label.clear()
            self.video_label.setText("Camera OFF")
            self.btn_start.setText("🚀 감시 시작")
            self.btn_start.setStyleSheet("background-color: #00c853; color: white; font-size: 18px; padding: 15px; border-radius: 8px;")
            self.is_running = False

    def beep(self):
        system_name = platform.system()
        if system_name == "Darwin":
            os.system('afplay /System/Library/Sounds/Ping.aiff &')
        elif system_name == "Windows":
            import winsound
            winsound.Beep(1000, 100)

    def update_frame(self):
        if self.cap is None: return
        ret, frame = self.cap.read()
        if not ret: return

        processed_image, status, color = self.monitor.process_frame(frame)
        
        if status != "Good":
            self.status_label.setText(f"🚨 {status}")
            self.status_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #ff3d00;")
            self.monitor.warning_duration += 1
            if self.monitor.warning_duration > 15:
                self.beep()
                self.monitor.warning_duration = 0
        else:
            self.status_label.setText("✅ 바른 자세")
            self.status_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #00e676;")
            self.monitor.warning_duration = 0

        h, w, ch = processed_image.shape
        bytes_per_line = ch * w
        qt_image = QImage(processed_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(qt_image))
        self.video_label.setScaledContents(True)

    # 종료 시 리포트 팝업
    def closeEvent(self, event):
        if self.monitor.total_frames > 0:
            bad_ratio = (self.monitor.bad_posture_frames / self.monitor.total_frames) * 100
            score = max(0, 100 - bad_ratio)
            seconds = self.monitor.total_frames // 30 # 대략적 시간
            
            msg = QMessageBox()
            msg.setWindowTitle("📊 오늘의 자세 리포트")
            msg.setText(f"수고하셨습니다.\n\n🕒 사용 시간: {seconds}초\n🐢 거북목 발생률: {bad_ratio:.1f}%\n\n💯 당신의 자세 점수는 [ {int(score)}점 ] 입니다.")
            msg.setIcon(QMessageBox.Information)
            msg.exec_()
            
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())