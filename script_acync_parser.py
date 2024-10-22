import aiohttp
import asyncio
from bs4 import BeautifulSoup
import datetime
import time
import pandas as pd
import os
import json
import re


cities = ['kharkov']
blocks = []
start_time = time.time()

async def get_links(session, sem, url, page_num):
    async with sem:
        link = url + '?page=' + str(page_num)
        try:
            async with session.get(link) as response:
                # search and add information about apartments from the script tag
                soup = BeautifulSoup(await response.text(), 'lxml')
                script = soup.find_all('script')[2].text.strip()[25:-122]
                info_block = json.loads(script)
                blocks.extend(info_block.get('catalog', {}).get('realtyForCatalog', []))
        except Exception as e:
            print("erorr 1")

async def gather_city_links():
    sem = asyncio.Semaphore(3)  # or 4 is optimal
    async with aiohttp.ClientSession() as session:
        tasks = []
        for city in cities:
            url = f'https://dom.ria.com/uk/arenda-kvartir/{city}/'
            async with session.get(url) as response:
                soup = BeautifulSoup(await response.text(), 'lxml')
                try:
                    str_page_counts = soup.find('span', class_='pagerMobileScroll')
                    counts_of_page = int(str_page_counts.find_all('a', class_='page-item button-border')[-1].text.strip())
                except (IndexError, ValueError):
                    counts_of_page = 1
                
                for page_num in range(1, counts_of_page + 1):
                    task = asyncio.create_task(get_links(session, sem, url, page_num))
                    tasks.append(task)
        
        await asyncio.gather(*tasks)

def main():
    asyncio.run(gather_city_links())
    cur_time = datetime.datetime.now().strftime('%d_%m_%Y_%H')

    flattened_list = []
    for data in blocks:
        # using method "get" I collect all necessary data for me
        street = data.get('street_name_uk')
        building_number = data.get('building_number_str')
        
        total_square =  data.get('total_square_meters')
        kitchen_square = data.get('kitchen_square_meters')
        living_square = data.get('living_square_meters')
        
        flat_floor = data.get('floor')
        total_floors = data.get('floors_count')
        rooms = data.get('rooms_count')
        
        price_uah = data.get('priceUAH')
        price_usd = data.get('priceUSD')
        
        wall_type = data.get('wall_type') 
        sleeps_pl = data.get('sleeps_count')
        
        latitude = data.get('latitude')    # latitude first / longitude second
        longitude = data.get('longitude')
        
        date = data.get('publishingDate')
        url = 'https://dom.ria.com/uk/' + str(data.get('beautiful_url'))

        photo_num = data.get('photos_count')
        zk_name = data.get('user_newbuild_name_uk')
        
        description = data.get('description_uk') or data.get('description')
        studio = 0
        if description:
            pattern = re.compile(r'(квартир[ау]\s*-?\s*студ[яіюї]|квартир[ау]\s*-?\s*студ[ияию])', re.IGNORECASE)
            match = pattern.search(description)
            if match:
                studio = 1

        city, main_district, sec_area, metro = None, None, None, None  # find info about flat location
        geo_blocks = data.get('cardRelink', [])
        for block in reversed(geo_blocks):
            if block.get('type') == 'city':
                city = block.get('anchor')
            elif block.get('type') == 'area' and main_district == None:
                main_district = block.get('anchor')
            elif block.get('type') == 'area' and main_district != None:
                sec_area = block.get('anchor')
            elif block.get('type') == 'metro':
                metro = block.get('anchor')
        
        # find data from adding features from website
        calm_area = 0
        quite_yard = 0
        park = 0
        new_renovation = 0
        center = 0
        possible_animal = 0
        near_metro = 0
        kitchen_st = 0
        secured_area = 0
        good_view = 0
        luxury_area = 0
        add_features = data.get('secondaryUtp', [])
        for feature in add_features:
            if isinstance(feature, dict):
                utp = feature.get('utp')
                if utp == 'Спокійний район':
                    calm_area = 1
                elif utp == 'Тихий двір':
                    quite_yard = 1
                elif utp == 'Поруч з парком':
                    park = 1
                elif utp == 'Новий ремонт':
                    new_renovation = 1
                elif utp == 'У центрі':
                    center = 1
                elif utp == 'Можна з тваринами':
                    possible_animal = 1
                elif utp == 'Поруч з метро':
                    near_metro = 1
                elif utp == 'Кухня-студія':
                    kitchen_st = 1
                elif utp == 'Територія охороняється':
                    secured_area = 1
                elif utp == 'Гарний краєвид':
                    good_view = 1
                elif utp == 'Престижний район':
                    luxury_area = 1
            else:
                continue

        info = {
            'Ціна оренди (грн)': price_uah,
            'Ціна оренда (usd)': price_usd,
            'Місто': city,
            'Район': main_district,
            'Мікрорайон': sec_area,
            'Метро': metro,
            'Вулиця': street,
            'Номер будинку': building_number,
            'Назва ЖК': zk_name,
            'Загальна площа': total_square,
            'Житлова площа': living_square,
            'Площа кухні': kitchen_square,
            'Поверх': flat_floor,
            'Всього поверхів': total_floors,
            'Кімнат': rooms,
            'Тип стін': wall_type,
            'Кількість фото': photo_num,
            'Студія': studio,
            'Спальні місця': sleeps_pl,
            'Широта': latitude,
            'Довгота': longitude,
            'Дата': date,
            'Посилання': url,
            'Опис': description,
            'Спокійний район': calm_area,
            'Тихий двір': quite_yard,
            'Поруч з парком': park,
            'Новий ремонт': new_renovation,
            'У центрі': center,
            'Можна з тваринами': possible_animal,
            'Поруч з метро': near_metro,
            'Кухня-студія': kitchen_st,
            'Територія охороняється': secured_area,
            'Гарний краєвид': good_view,
            'Престижний район': luxury_area
        }

        flattened_list.append(info)

    df = pd.DataFrame(flattened_list)
    curr_direct = os.path.dirname(os.path.abspath(__file__))
    cur_time = datetime.datetime.now().strftime("%d_%m_%Y_%H")
    df.to_csv(os.path.join(curr_direct, f"flat_info_{cur_time}.csv"), index=False)

    print(len(flattened_list))
    finish_time = time.time() - start_time
    print(f"The time spent on the script: {round(finish_time, 2)}")

if __name__=="__main__":
    main()

# total data by kharkiv: 1043
# The time spent on the script: 54.9
