import time
from typing import List, Dict
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

class KanjiScraper:
    def __init__(self):
        self.base_url = "https://nihongoi.com"
        
        # Chrome 옵션 설정
        chrome_options = Options()
        # chrome_options.add_argument('--headless')  # 브라우저 창을 띄우도록 변경
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        # WebDriver 초기화
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        self.kanji_data = {}

    def get_kanji_list(self, level: int, sublevel: int) -> List[Dict]:
        url = f"{self.base_url}/ko/kanji/list/{level}-{sublevel}"
        print(f"Fetching page: {url}")
        
        try:
            self.driver.get(url)
            time.sleep(3)  # 페이지 로딩 대기 시간
            
            # "모든 정답 표시" 버튼들을 찾아서 클릭
            buttons = self.driver.find_elements(By.CLASS_NAME, 'toggle-answer')
            print(f"Found {len(buttons)} toggle buttons")
            
            # 모든 정답을 표시하는 JavaScript 코드 실행
            self.driver.execute_script("""
                document.querySelectorAll('.correct-answer').forEach(function(el) {
                    el.style.display = 'block';
                });
            """)
            time.sleep(2)  # JavaScript 실행 대기
            
            # 한자 카드들을 찾습니다
            kanji_cards = self.driver.find_elements(By.CLASS_NAME, 'kanji-item')
            print(f"Found {len(kanji_cards)} kanji cards")
            kanji_list = []
            
            for i, card in enumerate(kanji_cards):
                try:
                    print(f"\nProcessing card {i+1}:")
                    
                    # 한자 (kanji-character 클래스에서 추출)
                    kanji = card.find_element(By.CLASS_NAME, 'kanji-character').text.strip()
                    print(f"Found kanji: {kanji}")
                    
                    # 읽기 (correct-answer 클래스에서 추출)
                    correct_answer = card.find_element(By.CLASS_NAME, 'correct-answer')
                    # display 스타일을 직접 변경
                    self.driver.execute_script("arguments[0].style.display = 'block';", correct_answer)
                    reading = correct_answer.text.strip()
                    print(f"Found reading: {reading}")
                    
                    # 번역 (translation 클래스에서 추출)
                    translation = card.find_element(By.CLASS_NAME, 'translation').text.strip()
                    translation = translation.replace('번역:', '').strip()  # "번역:" 텍스트 제거
                    print(f"Found translation: {translation}")
                    
                    if kanji and reading and translation:
                        kanji_data = {
                            "단어": kanji,
                            "읽기": reading,
                            "뜻": translation
                        }
                        kanji_list.append(kanji_data)
                        print(f"Added kanji: {kanji} ({reading}) - {translation}")
                except Exception as e:
                    print(f"Error parsing kanji card {i+1}: {e}")
                    print("Error details:", str(e))
                    continue
            
            print(f"\nExtracted {len(kanji_list)} kanji from this page")
            if kanji_list:
                return kanji_list
            return []
            
        except Exception as e:
            print(f"Error loading page: {e}")
            print("Error details:", str(e))
            return []

    def scrape_all_levels(self):
        # 웹사이트의 실제 레벨 구조에 맞게 수정
        levels = {
            "레벨 1 (JLPT N5)": range(1, 25),      # 1-1부터 1-24까지
            "레벨 2 (JLPT N5-N4)": range(1, 25),   # 2-1부터 2-24까지
            "레벨 3 (JLPT N5-N3)": range(1, 25),   # 3-1부터 3-24까지
            "레벨 4 (JLPT N4-N2)": range(1, 25),   # 4-1부터 4-24까지
            "레벨 5 (JLPT N3-N1)": range(1, 25),   # 5-1부터 5-24까지
            "레벨 6 (JLPT N2-N1)": range(1, 25)    # 6-1부터 6-24까지
        }

        try:
            for level_name, sublevels in levels.items():
                level_num = int(level_name.split()[1])
                self.kanji_data[level_name] = {}
                print(f"\n=== {level_name} 스크래핑 시작 ===")
                
                for sublevel in sublevels:
                    print(f"\n=== 스크래핑 시작: 레벨 {level_num}-{sublevel} ===")
                    kanji_list = self.get_kanji_list(level_num, sublevel)
                    if kanji_list:
                        self.kanji_data[level_name][f"레벨 {level_num}-{sublevel}"] = kanji_list
                        self.save_to_json()  # 각 서브레벨마다 저장
                        print(f"=== 성공적으로 스크랩 완료: 레벨 {level_num}-{sublevel} ===\n")
                    else:
                        print(f"=== 데이터를 찾을 수 없음: 레벨 {level_num}-{sublevel} ===\n")
                        # 데이터가 없는 경우 해당 레벨의 스크래핑 중단
                        break
                    
                    time.sleep(2)  # 서버 부하 방지를 위해 대기 시간 증가
                
                print(f"=== {level_name} 스크래핑 완료 ===\n")
        finally:
            input("Press Enter to close the browser...")  # 브라우저를 바로 닫지 않고 대기
            self.driver.quit()  # 브라우저 종료

    def save_to_json(self, filename: str = "kanji_data.json"):
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.kanji_data, f, ensure_ascii=False, indent=2)
            print(f"Data saved to {filename}")
            # 저장된 데이터 확인
            with open(filename, 'r', encoding='utf-8') as f:
                saved_data = json.load(f)
                print(f"Verified saved data: {json.dumps(saved_data, ensure_ascii=False, indent=2)}")
        except Exception as e:
            print(f"Error saving data to {filename}: {e}")

def main():
    scraper = KanjiScraper()
    scraper.scrape_all_levels()

if __name__ == "__main__":
    main() 