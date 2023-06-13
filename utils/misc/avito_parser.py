import asyncio
import datetime
import random
import threading
import time

from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By

from loader import bot, dp
from utils.db_api import quick_cmd_urls


async def start_parse():
    urls = await quick_cmd_urls.select_all_urls()
    for url in urls:
        if url.in_parse:
            threading.Thread(target=parsing_urls, args=(url.url, url.name, url.user_id)).start()


def parsing_urls(url: str, name_parse, user_id):
    print("Start parsing", datetime.datetime.now())
    options = webdriver.ChromeOptions()
    options.add_argument("user-agent=Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument('log-level=3')
    options.add_argument("--headless")  # прячет браузер от глаз
    options.add_argument("--no-sandbox")
    prefs = {"profile.managed_default_content_settings.images": 2}  # не загружает картинки
    options.add_experimental_option("prefs", prefs)
    options.page_load_strategy = 'eager'  # ожидание загрузки скриптов
    PROXY = "149.126.234.123:8000"  # IP:PORT or HOST:PORT
    options.add_argument('--proxy-server=%s' % PROXY)
    browser = webdriver.Chrome(options=options)
    browser.implicitly_wait(10)
    browser.set_window_size(200, 10000)

    flag_first_msg = False
    count_exeptions = 0
    counter = 0
    while True:
        print(counter, datetime.datetime.now(), name_parse)
        if not flag_first_msg:
            asyncio.run_coroutine_threadsafe(quick_cmd_urls.remove_items_list(user_id, name_parse),
                                             dp.loop)
        try:
            counter += 1
            if counter % 50 == 0:
                asyncio.run_coroutine_threadsafe(
                    bot.send_message(user_id, f"{name_parse}" + "\nЯ работаю!"), dp.loop)
            if not asyncio.run_coroutine_threadsafe(quick_cmd_urls.check_name_url(user_id, name_parse),
                                                    dp.loop).result():
                browser.close()
                browser.quit()
                return
            items = asyncio.run_coroutine_threadsafe(quick_cmd_urls.get_items_list(user_id, name_parse),
                                                    dp.loop).result()
            print("---------", len(items))
            browser.get(url)
            time.sleep(random.randrange(5, 8))
            try:
                browser.find_element(By.CSS_SELECTOR, '[class="no-results-root-bWQVm"]')
                if counter % 50 == 0:
                    asyncio.run_coroutine_threadsafe(
                        bot.send_message(user_id, f"{name_parse}" + "\nРезультатов на странице нет!"), dp.loop)
                continue
            except NoSuchElementException:
                pass
            try:
                item_list = browser.find_element(By.CSS_SELECTOR, '[data-marker="catalog-serp"]')
                items_new = item_list.find_elements(By.CSS_SELECTOR, '[data-marker="item"]')
            except NoSuchElementException:
                print(f"Exception, ban ip! {datetime.datetime.now()}")
                count_exeptions += 1
                browser.set_window_size(1920, 1080)
                browser.get_screenshot_as_file(f"screenshots/{name_parse + '_BANIP_' + str(count_exeptions)}.png")
                browser.set_window_size(200, 10000)
                if count_exeptions == 10:
                    asyncio.run_coroutine_threadsafe(
                        bot.send_message(user_id, f"{name_parse}" + "\nОшибка на странице(ban ip)!"), dp.loop)
                    browser.close()
                    browser.quit()
                    threading.Thread(target=parsing_urls, args=(url, name_parse, user_id)).start()
                    return
                continue

            for item in reversed(items_new):
                href = item.find_element(By.CSS_SELECTOR, '[itemprop="url"]').get_attribute("href")
                if href not in items:
                    asyncio.run_coroutine_threadsafe(quick_cmd_urls.add_item_to_list(user_id, name_parse, href),
                                                     dp.loop)
                    if flag_first_msg:
                        try:
                            price = item.find_element(By.CSS_SELECTOR, '[itemprop="price"]').get_attribute("content")
                        except:
                            price = 0
                        try:
                            name = item.find_element(By.CSS_SELECTOR, '[itemprop="name"]').text
                        except:
                            name = "Не удалось получить название"
                        href_to_send = "www.avito.ru/" + href.split("_")[-1].split("?")[0]
                        try:
                            img = item.find_element(By.CSS_SELECTOR, '[itemprop="image"]').get_attribute("src")
                        except:
                            img = open('no-photo.jpg', 'rb')
                        asyncio.run_coroutine_threadsafe(
                            bot.send_photo(chat_id=user_id, photo=img,
                                           caption=f"{price}✅{name}\n*{name_parse}*\n#{name_parse.replace(' ', '')}\n"
                                                   f"Ссылка на объявление: {href_to_send}",
                                           parse_mode="Markdown"),
                                                         dp.loop)
            if not flag_first_msg:
                try:
                    browser.find_element(By.CSS_SELECTOR, '[data-marker="pagination-button"]')
                    if "p=1" in url:
                        url_page2 = url.replace("p=1", "p=2")
                    else:
                        url_page2 = url + "&p=2"
                    browser.get(url_page2)
                    time.sleep(random.randrange(5, 8))
                    browser.implicitly_wait(10)
                    for i in range(0, 10):
                        try:
                            item_list = browser.find_element(By.CSS_SELECTOR, '[data-marker="catalog-serp"]')
                            items_new = item_list.find_elements(By.CSS_SELECTOR, '[data-marker="item"]')
                        except NoSuchElementException:
                            print(f"Exception, ban ip! {datetime.datetime.now()}")
                            if i == 9:
                                browser.close()
                                browser.quit()
                                threading.Thread(target=parsing_urls,
                                                 args=(url, name_parse, user_id)).start()
                                return
                            continue
                        break
                except NoSuchElementException:
                    pass
                for item in items_new:
                    href = item.find_element(By.CSS_SELECTOR, '[itemprop="url"]').get_attribute("href")
                    if href not in items:
                        asyncio.run_coroutine_threadsafe(quick_cmd_urls.add_item_p2_to_list(user_id, name_parse, href),
                                                         dp.loop)
            flag_first_msg = True
        except Exception as e:
            browser.set_window_size(1920, 1080)
            browser.get_screenshot_as_file(f"screenshots/exp{datetime.datetime.now()}.png")
            browser.set_window_size(200, 10000)
            asyncio.run_coroutine_threadsafe(
                bot.send_message(user_id, f"{name_parse}" + "\nОшибка в получении страницы!"), dp.loop)
            try:
                browser.close()
                browser.quit()
            except:
                print(f"Браузер закрыт! {datetime.datetime.now()}")
            threading.Thread(target=parsing_urls, args=(url, name_parse, user_id)).start()
            print(f"Exception in get page! {datetime.datetime.now()}")
            return
