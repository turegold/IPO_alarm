# 📊 공모주 일정 · 수익 분석 알림 시스템 (IPO Alarm)

공모주(IPO) 청약 과정에서 발생하는 **일정 확인, 정보 수집, 청약 관리, 수익 정리** 작업을  
하나의 데스크톱 프로그램에서 자동화하기 위해 개발한 **Python 기반 GUI 애플리케이션**입니다.

---

## ✨ 주요 기능

- 📅 **월별 공모주 일정 자동 수집**
  - 금융 정보 사이트(ipostock)에서 공모주 일정 크롤링
  - 종목명, 청약 일정, 상장일, 주관사, 상세 정보 제공
<img width="569" height="398" alt="Image" src="https://github.com/user-attachments/assets/cc5ebb57-f2db-449d-a8a9-ac8f3bcd372a" />
<img width="558" height="442" alt="image" src="https://github.com/user-attachments/assets/cf558fb9-e15e-4b89-b4fe-dd9a02d8b295" />


- 📝 **청약 예정 / 청약 완료 관리**
  - 관심 종목을 청약 예정 또는 완료 상태로 관리
  - 메모 작성 및 종목별 알림 ON/OFF 설정 가능
<img width="605" height="425" alt="image" src="https://github.com/user-attachments/assets/ba486966-a7f3-49f9-a503-e900728e8bdb" />

- 💰 **청약 완료 후 수익 기록**
  - 배정 수량, 매수가, 매도가 입력
  - 수익 및 수익률 자동 계산
<img width="604" height="393" alt="image" src="https://github.com/user-attachments/assets/9b7c64e3-9d93-4230-a324-0862aaf13be2" />

- 📈 **월별 수익 분석**
  - 연도별 · 월별 총 수익 / 평균 수익률 / 종목 수 분석
  - CSV 및 PDF 리포트 자동 생성
<img width="605" height="392" alt="image" src="https://github.com/user-attachments/assets/7b8eae49-533e-4459-aa63-36efda16db9a" />

- 🔔 **디스코드 알림 기능**
  - 청약 시작일, 상장일 자동 알림
  - 웹훅 URL 설정, 테스트 메시지, 디버그 실행 지원
<img width="605" height="581" alt="image" src="https://github.com/user-attachments/assets/5de60258-a8ee-4ea5-84c9-23cfa3243241" />

---

## 🛠 사용 기술

- **Language**: Python 3.12
- **GUI**: PyQt6
- **Web Crawling**: requests, BeautifulSoup
- **Data Storage**: JSON
- **Visualization & Report**: matplotlib, fpdf2
- **Notification**: Discord Webhook

---




