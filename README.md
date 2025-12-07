# 🐢 Smart Posture Keeper (거북목 지킴이)

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![PyQt5](https://img.shields.io/badge/GUI-PyQt5-green)
![MediaPipe](https://img.shields.io/badge/AI-MediaPipe-orange)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

📖 프로젝트 소개
현대인의 고질병인 “거북목 증후군(Turtle Neck Syndrome)”을 예방하기 위한 AI 기반 실시간 자세 교정 프로그램이다.
웹캠을 통해 사용자의 자세를 실시간으로 분석하고, 거북목 자세나 졸음이 감지되면 즉시 알림을 제공한다.
사용자별 맞춤형 감도 조절 기능을 제공하며, 
일일 자세 리포트 기능을 통해 지속적인 습관 교정을 돕고자 한다.


✨ 주요 기능
## 1. 실시간 거북목 & 졸음 감지
- Google MediaPipe의 Pose & Face Mesh 모델을 활용하여 98% 이상의 정확도로 관절 위치를 추적한다.
- 사용자가 모니터 앞으로 목을 빼거나, 눈을 감고 졸면 즉시 시각적 경고(붉은 화면)와 청각적 알림(비프음)이 작동한다.

## 2. 개인화된 감도 조절 (슬라이더 제공)
- 사람마다 다른 앉은키와 카메라 위치를 고려하여, 슬라이더(Slider)를 이용하여 민감도를 0.01 단위로 미세 조절할 수 있다.
- 사용자에게 딱 맞는 정자세 기준을 설정할 수 있어 오작동을 최소화했다.

## 3. 오늘의 자세 리포트 (Feedback System)
- 프로그램을 종료할 때, 사용 시간과 거북목 유지 비율을 분석하여 '자세 점수(100점 만점)'를 보여준다.
- 수치화된 피드백을 통해 사용자가 자신의 습관을 객관적으로 인지하게 한다.


## 💻 실행 화면
| 감시 시작 (정상) | 거북목 경고 (Turtle Neck) | 자세 리포트 (종료 시) |
|:---:|:---:|:---:|
| ![Main1](demo1.png) <br> ![Main2](demo2.png) | ![Warning1](demo3.png) <br> ![Warning2](demo4.png) | ![Report](demo5.png) |

> 위 이미지는 실제 구동 화면입니다.

## 🛠 기술 스택
- Language: Python 3.10
- AI Core: MediaPipe, OpenCV (Computer Vision)
- GUI Framework: PyQt5 (User Friendly Interface)
- Algorithm: EAR(Eye Aspect Ratio) for Drowsiness, Vector Analysis for Posture


## 🚀 설치 및 실행 방법
```bash
# 1. 저장소 클론
git clone https://github.com/sulchive/Smart-Posture-Keeper

# 2. 필수 라이브러리 설치
pip install -r requirements.txt

# 3. 프로그램 실행
python final_app.py


## 이 프로젝트는 MIT License를 따릅니다. 자세한 내용은 LICENSE 파일을 참고하세요.

