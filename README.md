
# 📬 메일 알리미

## ✅ 프로젝트 개요

로컬 환경에서 메일 수신을 자동 감지하고, 특정 조건에 맞는 메일의 발신자 및 제목을 확인한 뒤
팝업 알림으로 사용자에게 알려주는 Python 기반 자동화 프로젝트입니다.
마지막 확인 시점을 기록하여 중복 처리를 방지하며, `.vbs`와 Windows 작업 스케줄러를 연동해
사용자 개입 없이도 정기적으로 실행되도록 구성하였습니다.

---

## 🛠 기술 스택

* Python 3.8
* `imaplib`, `email`, `pyyaml`, `tkinter`
* `.bat` 실행 스크립트
* `.vbs` 자동 실행 스크립트
* Windows 작업 스케줄러

---

## 🧩 기능 구조

* `config.yaml`에서 필터 조건 (제목 키워드, 발신자 이메일) 불러오기
* IMAP을 통해 받은편지함 메일 조회
* `last_checked.yaml`에 마지막 확인 시각 저장
* 조건 충족 메일 필터링
* 중복 방지 처리 (이전 시각보다 이후 메일만 확인)
* 필터 통과 시 팝업 알림 (`tkinter.messagebox`) 실행
* `.bat` + `.vbs` 연계로 CMD 창 없이 백그라운드 실행 가능
* Windows 작업 스케줄러를 통해 정기 실행 가능

---

## 🧪 시나리오 예시

* 회사 메일 계정으로 회의록/견적서 메일이 수신됨
* 필터에 등록된 제목 키워드 (`"회의록"`, `"긴급"`) 또는 발신자 (`boss@company.com`)와 일치
* 메일 확인 시 팝업으로 즉시 알림
* `last_checked.yaml`에 자동으로 수신 시각 업데이트 → 중복 알림 없음
* 작업 스케줄러를 통해 5분마다 `.vbs`가 `.bat`을 호출해 메일 확인 자동화 진행

---

## 📂 파일 구성

| 파일명                  | 설명                                    |
| -------------------- | ------------------------------------- |
| `main.py`            | 메일 필터링 및 알림 실행 진입점                    |
| `mail_handler.py`    | 메일 조회, 파싱, 필터링 및 시간 기록 로직             |
| `kakao_alert.py`     | 팝업 알림 함수 (`tkinter` 기반)               |
| `config.yaml`        | 제목 키워드, 발신자 리스트 등 조건 설정 파일            |
| `last_checked.yaml`  | 마지막 확인 시각 자동 저장 (자동 생성됨)              |
| `run_mail_check.bat` | 실제 실행되는 Python 실행용 스크립트               |
| `run_mail_check.vbs` | `.bat`을 CMD 창 없이 호출하는 스크립트 (스케줄러 연동용) |

---

## 🎯 결과

* 전체 자동화 파이프라인을 로컬 PC에 완전하게 구성
* 반복적인 수동 메일 체크 업무 제거
* Windows 환경에서 `.vbs + 작업 스케줄러` 기반으로 안정적 자동 실행 가능
* 메시지 중복 처리 방지 → 업무 신뢰도 및 사용자 만족도 향상
* YAML 설정으로 조건 변경도 코드 수정 없이 유연하게 대응 가능

---

## 🧠 느낀 점: "자동화는 실사용 가능할 때 의미가 생긴다"

* 이번 프로젝트는 단순히 코드로 자동화를 구현하는 것이 아닌,
  **실제 업무 흐름에 자동화를 안정적으로 '붙이는 것'에 초점을 맞췄다.**
* 필터 조건과 중복 방지, 알림까지의 흐름을 만들면서
  \*\*“작동하는 자동화와 쓰이는 자동화는 다르다”\*\*는 걸 느꼈다.
* `.vbs` 실행, Windows 작업 스케줄러, YAML 설정 파일 등
  **개발이 아닌 운영 관점에서 자동화를 설계**하였다.
* 특히 마지막 확인 시점을 기준으로 메일을 선별하는 로직을 통해
  자동화는 무조건 반복하는 게 아니라, **타이밍과 조건을 구성하는 일**임을 알게 되었다.
* 개발자 입장에서는 작아 보일 수 있지만,
  **사용자 입장에서는 “필요한 메일만 받는다”는 확신을 주는 경험**이었다.

