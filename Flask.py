from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)  # 모든 도메인에서 요청 허용
socketio = SocketIO(app, cors_allowed_origins="*")  # WebSocket 활성화

# SQLite 데이터베이스 연결 함수
def connect_db():
    return sqlite3.connect('checkin_system.db')

# 모든 기록 반환
@app.route('/records', methods=['GET'])
def get_records():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, checkin_time, checkout_time FROM users')
    records = cursor.fetchall()
    conn.close()

    result = []
    for record in records:
        if record[2] is not None and record[3] is None:
            status = "Check-in"
            time = record[2]
        elif record[3] is not None:
            status = "Check-out"
            time = record[3]
        else:
            continue
        result.append({
            "id": record[0],
            "name": record[1],
            "time": time,
            "status": status
        })
    return jsonify(result)

# 새로운 기록 추가
@app.route('/add_record', methods=['POST'])
def add_record():
    data = request.get_json()
    id_value = data['id']
    name = data.get('name', '')
    status = data['status']
    time = data['time']

    conn = connect_db()
    cursor = conn.cursor()

    if status == "Check-in":
        cursor.execute('''
            INSERT OR REPLACE INTO users (id, name, checkin_time, checkout_time)
            VALUES (?, ?, ?, NULL)
        ''', (id_value, name, time))
    elif status == "Check-out":
        cursor.execute('''
            UPDATE users
            SET checkout_time = ?
            WHERE id = ?
        ''', (time, id_value))

    conn.commit()
    conn.close()

    # WebSocket을 통해 React에 실시간 데이터 전송
    message = {'id': id_value, 'name': name, 'time': time, 'status': status}
    print("WebSocket 메시지 전송:", message)  # 디버깅용 메시지 출력
    socketio.emit('update', message)  # JSON 데이터 전송

    return jsonify({"message": "Record added successfully!"}), 200

if __name__ == '__main__':
    socketio.run(app, debug=True)
