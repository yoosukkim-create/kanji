# 일본어 한자 스크래퍼

nihongoi.com에서 JLPT 레벨별 한자 데이터를 수집하는 Python 스크래퍼입니다.

## 기능
- JLPT 레벨별 한자 데이터 수집
- 한자, 읽기(음독/훈독), 한국어 의미 추출
- JSON 형식으로 데이터 저장

## 설치 방법

1. 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. 필요한 패키지 설치
```bash
pip install selenium
```

3. Chrome WebDriver 설치
```bash
# macOS (Homebrew)
brew install chromedriver

# Windows
# Chrome 버전에 맞는 WebDriver를 수동으로 설치해야 합니다.
```

## 사용 방법

```bash
python kanji_scraper.py
```

## 출력 데이터 형식

```json
{
  "레벨 1 (JLPT N5)": {
    "레벨 1-1": [
      {
        "단어": "漢字",
        "읽기": "かんじ",
        "뜻": "한자"
      }
    ]
  }
}
```

## 주의사항

- 웹사이트의 robots.txt를 준수해주세요.
- 과도한 요청을 피하기 위해 각 요청 사이에 1초의 딜레이가 있습니다.
- 기본적으로 처음 10페이지만 스크래핑합니다. 