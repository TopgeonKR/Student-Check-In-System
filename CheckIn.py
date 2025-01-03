import tkinter as tk
from tkinter import messagebox
import sqlite3
import cv2
from pyzbar.pyzbar import decode
from datetime import datetime
import requests
import threading

# SQLite 데이터베이스 초기화
def initialize_db():
    conn = sqlite3.connect('checkin_system.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            name TEXT,
            checkin_time TEXT,
            checkout_time TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Flask 서버로 데이터 전송
def send_to_flask(id_value, name, status):
    url = "http://localhost:5000/add_record"
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = {
        "id": id_value,
        "name": name,
        "status": status,
        "time": current_time
    }
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            print("Flask 서버로 데이터 전송 성공:", data)
        else:
            print("Flask 서버로 데이터 전송 실패:", response.text)
    except Exception as e:
        print("Flask 서버로 데이터 전송 중 오류 발생:", e)

# 바코드 스캔 함수
def scan_barcode():
    def run_camera():
        global camera_active
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            messagebox.showerror("Error", "카메라를 열 수 없습니다. 카메라 설정을 확인하세요.")
            camera_active = False
            camera_window.destroy()
            return None

        id_scanned = None
        while camera_active:
            ret, frame = cap.read()
            if not ret:
                messagebox.showerror("Error", "카메라에서 프레임을 읽을 수 없습니다.")
                break

            # 화면 중앙에 가이드 사각형 그리기
            height, width, _ = frame.shape
            start_point = (width // 4, height // 3)
            end_point = (width * 3 // 4, height * 2 // 3)
            color = (0, 255, 0)  # 초록색
            thickness = 2
            cv2.rectangle(frame, start_point, end_point, color, thickness)

            # 바코드 디코딩
            decoded_objects = decode(frame)
            for obj in decoded_objects:
                id_scanned = obj.data.decode("utf-8")  # 바코드 데이터를 문자열로 디코딩
                messagebox.showinfo("Success", f"바코드 인식 성공: {id_scanned}")
                camera_active = False
                send_to_flask(id_scanned, "", "Check-in")  # Flask 서버로 데이터 전송
                break

            # 프레임을 화면에 표시
            cv2.imshow("Scan Barcode", frame)

            # 'q' 키를 누르면 종료
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

        # 카메라 창 닫기
        if id_scanned is not None:
            camera_window.destroy()

    def stop_camera():
        global camera_active
        camera_active = False
        camera_window.destroy()

    # 카메라 실행 플래그 설정
    global camera_active
    camera_active = True

    # 새 Tkinter 창 생성
    camera_window = tk.Toplevel(root)
    camera_window.title("카메라 실행 중")

    # 종료 버튼 추가
    stop_button = tk.Button(camera_window, text="카메라 종료", command=stop_camera)
    stop_button.pack()

    # OpenCV 스레드 시작
    camera_thread = threading.Thread(target=run_camera)
    camera_thread.start()

# 체크인 함수
def check_in():
    id_value = entry_id.get()
    name_value = entry_name.get()

    if not id_value:
        messagebox.showerror("Error", "ID를 입력하세요.")
        return
    send_to_flask(id_value, name_value, "Check-in")

# 체크아웃 함수
def check_out():
    id_value = entry_id.get()

    if not id_value:
        messagebox.showerror("Error", "ID를 입력하세요.")
        return
    send_to_flask(id_value, "", "Check-out")

# Tkinter GUI 설정
root = tk.Tk()
root.title("학생 체크인 시스템")

# ID 및 이름 입력
tk.Label(root, text="ID:").grid(row=0, column=0)
entry_id = tk.Entry(root)
entry_id.grid(row=0, column=1)

tk.Label(root, text="Name:").grid(row=1, column=0)
entry_name = tk.Entry(root)
entry_name.grid(row=1, column=1)

# 버튼
btn_scan = tk.Button(root, text="바코드 스캔", command=scan_barcode)
btn_scan.grid(row=0, column=2)

btn_checkin = tk.Button(root, text="체크인", command=check_in)
btn_checkin.grid(row=2, column=0)

btn_checkout = tk.Button(root, text="체크아웃", command=check_out)
btn_checkout.grid(row=2, column=1)

# 데이터베이스 초기화
initialize_db()

# Tkinter 루프 시작
root.mainloop()
