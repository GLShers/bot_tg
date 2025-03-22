from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def search_tgstat(query):
    url = "https://tgstat.ru/channels/search"
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Запуск без графического интерфейса
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--user-agent=Mozilla/5.0")  # Имитация реального пользователя
    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get(url)
        
        # Ждем появления поля поиска
        try:
            search_input = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']"))
            )
        except:
            print("Не удалось найти поле поиска.")
            return []
        
        search_input.send_keys(query)
        time.sleep(1)  # Небольшая задержка перед поиском
        
        # Клик по кнопке поиска (если есть)
        try:
            search_button = driver.find_element(By.CSS_SELECTOR, "button.btn-primary")
            driver.execute_script("arguments[0].click();", search_button)
        except:
            search_input.send_keys(Keys.RETURN)
        
        time.sleep(3)  # Ждём загрузку результатов
        
        channels = []
        results = driver.find_elements(By.CSS_SELECTOR, "div.card-body")
        
        for item in results:
            try:
                name_elem = item.find_element(By.CSS_SELECTOR, "div.text-truncate.font-16.text-dark.mt-n1")
                name = name_elem.text.strip()
                link_elem = item.find_element(By.CSS_SELECTOR, "a[href*='/channel/']")
                link = link_elem.get_attribute("href")
                
                # Переход на страницу канала
                driver.get(link)
                time.sleep(2)
                
                # Извлекаем @username
                try:
                    username_elem = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "h1 span"))
                    )
                    username = username_elem.text.strip()
                except:
                    username = "Не найдено"
                
                channels.append({"name": name, "username": username, "link": link})
                driver.back()
                time.sleep(2)
            except:
                continue
        
        return channels
    
    finally:
        driver.quit()

if __name__ == "__main__":
    query = input("Введите поисковый запрос: ")
    results = search_tgstat(query)
    
    if results:
        for channel in results:
            print(f"Название: {channel['name']}, Username: {channel['username']}, Ссылка: {channel['link']}")
    else:
        print("Каналы не найдены.")