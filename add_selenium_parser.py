# This script parse additional data from page on the dimria

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import os
import time
import datetime
import pandas as pd
import re

start_time = time.time()
features_data = []
total_data = []

def scrape_add_content_and_concat(html_content, row_record):
    soup = BeautifulSoup(html_content, "lxml")

    features = soup.find_all("ul", class_="unstyle main-list")
    cleaned_features = [
        part.strip()
        for item in features
        for div in item.find_all("div", class_="size18")
        for cleaned_item in re.sub(r'\s*\xa0·\xa0\s*|\n+', ' · ', div.get_text().strip()).split('·')
        for part in [cleaned_item.strip()]
    ]

    type_offer = None
    winter_payment = None
    summer_payment = None
    year_of_build = None
    pet = 0
    service_commission = 0
    type_of_wall_description = None

    for feature in cleaned_features:
        if "Пропозиція від" in feature:
            type_offer = feature
        elif "Комісія за послуги" in feature:
            service_commission = feature
        elif "взимку" in feature:
            winter_payment = int(re.search(r'\d+', feature).group())
        elif "влітку" in feature:
            summer_payment = int(re.search(r'\d+', feature).group())
        elif "Побудовано" in feature:
            years = re.findall(r'\d{4}', feature)
            year_of_build = max(map(int, years)) if years else None
        elif "Можна з тваринами" in feature:
            pet = 1
        elif "Стіни з" in feature:
            type_of_wall_description = feature.replace("Стіни з ", "")

    heat_type, water_heat_type, apartment_type, add_stuff, type_location, planning_feature, elevator = None, None, None, None, None, None, None
    try:
        add_info = soup.find("ul", {"id": "additionalInfo"})  # TRY
        all_add_features = add_info.find_all("div", class_="boxed")
        for feature in all_add_features:
            feature_txt = feature.get_text()
            if "Опалення:" in feature_txt:
                heat_type = feature_txt.replace("Опалення:", "").strip().replace("\xa0 •\xa0 ", "|")
            elif "Підігрів води:" in feature_txt:
                water_heat_type = feature_txt.replace("Підігрів води:", "").strip().replace("\xa0 •\xa0 ", "|")
            elif "Приміщення:" in feature_txt:
                apartment_type = feature_txt.replace("Приміщення:", "").strip().replace("\xa0 •\xa0 ", "|")
            elif "Обладнання" in feature_txt and "меблі" in feature_txt: 
                add_stuff = add_stuff = feature_txt.strip()[37:].strip().replace("\xa0 •\xa0 ", "|")
            elif "Розташування і оточення:" in feature_txt:
                type_location = feature_txt.replace("Розташування і оточення:", "").strip().replace("\xa0 •\xa0 ", "|")
            elif "Особливості планування:" in feature_txt:
                planning_feature = feature_txt.replace("Особливості планування:", "").strip().replace("\xa0 •\xa0 ", "|")
            elif "Ліфт:" in feature_txt:
                elevator = feature_txt.replace("Ліфт:", "").strip().replace("\xa0 •\xa0 ", "|")
    except Exception:
        pass
    
    try:
        agency = soup.find("div", class_='table p-rel hover-bg').find("div", class_="t-cell v-middle p-rel").find("b").get_text()
    except Exception:
        agency = None

    feature_data = {
        "Тип пропозиції": type_offer,
        "Комуналка взимку": winter_payment,
        "Комуналка влітку": summer_payment,
        "Рік побудови": year_of_build,
        "Тварини (опис)": pet,
        "Комісія": service_commission,
        "Тип стіни (опис)": type_of_wall_description,
        "Опалення": heat_type,
        "Підігрів води": water_heat_type,
        "Приміщення": apartment_type,
        "Зручності": add_stuff,
        "Розташування": type_location,
        "Планування": planning_feature,
        "Ліфт": elevator,
        "Агенство": agency
    }

    dict_row_record = dict(row_record)
    dict_row_record.update(feature_data)
    total_data.append(dict_row_record)

def get_html(driver, uri):
    driver.get(uri)
    time.sleep(3)
    return driver.page_source

def main():
    curr_direct = os.path.dirname(os.path.abspath(__file__))
    csv_file_path = os.path.join(curr_direct, "new_info_15_09_2024_22.csv")
    df = pd.read_csv(csv_file_path)

    driver_path = "C:/Users/dmytro/Documents/python_lessons/real_estate_selenium/chromedriver.exe"
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service)

    for i in range(len(df)):
        row_record = df.iloc[i, :]
        uri = df.iloc[i, 22]
        html_content = get_html(driver=driver, uri=uri)
        scrape_add_content_and_concat(html_content, row_record)
    
    driver.quit()
    current_time = datetime.datetime.now().strftime("%d_%m_%Y_%H")
    final_df = pd.DataFrame(total_data)
    final_df.to_csv(os.path.join(curr_direct, f"full_flats_info_{current_time}.csv"), index=False)
    
    finish_time = time.time() - start_time
    print(f"Wasted time: {round(finish_time, 2)}")

if __name__ == "__main__":
    main()

# Wasted time: 3472.54
# Can improve this part with Selenium Grid using Docker