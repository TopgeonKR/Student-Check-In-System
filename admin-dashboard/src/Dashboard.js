import React, { useEffect, useState } from "react";
import axios from "axios";

function Dashboard() {
  const [records, setRecords] = useState([]); // 기록 저장

  // WebSocket 설정
  useEffect(() => {
    const socket = new WebSocket("ws://localhost:5000/socket.io/?EIO=4&transport=websocket");

    // WebSocket 연결 성공
    socket.onopen = () => {
      console.log("WebSocket 연결 성공!");
    };

    // WebSocket 연결 오류
    socket.onerror = (error) => {
      console.error("WebSocket 오류:", error);
    };

    // WebSocket 메시지 수신
    socket.onmessage = (event) => {
      try {
        console.log("WebSocket 메시지 수신:", event.data);
        const parsedData = JSON.parse(event.data); // 메시지를 JSON으로 변환
        console.log("파싱된 데이터:", parsedData);

        if (parsedData.status) {
          setRecords((prevRecords) => [parsedData, ...prevRecords]); // 새로운 기록 추가
        }
      } catch (error) {
        console.error("WebSocket 메시지 처리 오류:", error, "원본 메시지:", event.data);
      }
    };

    // WebSocket 연결 종료
    socket.onclose = () => {
      console.log("WebSocket 연결 종료");
    };

    // 컴포넌트 언마운트 시 WebSocket 닫기
    return () => {
      socket.close();
    };
  }, []);

  // 초기 기록 가져오기
  useEffect(() => {
    const fetchRecords = async () => {
      try {
        const response = await axios.get("http://localhost:5000/records");
        setRecords(response.data); // 초기 기록 설정
        console.log("초기 기록 가져오기 성공:", response.data);
      } catch (error) {
        console.error("초기 기록 가져오기 오류:", error);
      }
    };

    fetchRecords();
  }, []);

  // React 작동 중 로그 출력
  useEffect(() => {
    const interval = setInterval(() => {
      console.log("React는 작동 중임");
    }, 5000); // 5초마다 로그 출력

    return () => clearInterval(interval); // 컴포넌트 언마운트 시 interval 정리
  }, []);

  // 기록을 테이블 형태로 렌더링
  return (
    <div style={{ padding: "20px" }}>
      <h1>관리자 대시보드</h1>
      <table border="1" style={{ width: "100%", textAlign: "left", borderCollapse: "collapse" }}>
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Time</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {records.map((record, index) => (
            <tr key={index}>
              <td>{record.id}</td>
              <td>{record.name || "N/A"}</td>
              <td>{record.time}</td>
              <td>{record.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default Dashboard;
