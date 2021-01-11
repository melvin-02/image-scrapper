import os
from selenium import webdriver
import time
import requests


def fetch_image_urls(search_term: str, n_links: int, web_driver: webdriver, sleep_between_interactions: int = 1):
    def scroll_to_end(web_driver):
        web_driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(sleep_between_interactions)

    search_url = f"https://www.google.com/search?tbm=isch&q={'+'.join(search_term.split())}"
    web_driver.get(search_url)

    image_counter = 0
    res_start = 0
    image_urls = set()

    while(image_counter < n_links):

        thumbnail_results = web_driver.find_elements_by_css_selector(
            'img.Q4LuWd')
        number_results = len(thumbnail_results)
        scroll_to_end(web_driver)
        print(
            f'Found {number_results} search results. Extracting links {res_start} to {number_results}')

        for img in thumbnail_results[res_start:number_results]:
            try:
                img.click()
                time.sleep(sleep_between_interactions)
            except:
                continue

            actual_image = web_driver.find_elements_by_css_selector(
                'img.n3VNCb')
            for img in actual_image:
                src = img.get_attribute('src')
                if src and 'http' in src:
                    image_urls.add(src)

            image_counter = len(image_urls)
            if image_counter >= n_links:
                print(f"Found {n_links} image links.")
                break

        else:
            print("Found:", len(image_urls),
                  "image links, looking for more ...")
            time.sleep(3)
            load_more_button = web_driver.find_element_by_css_selector(
                ".mye4qd")
            if load_more_button:
                web_driver.execute_script(
                    "document.querySelector('.mye4qd').click();")

        res_start = len(thumbnail_results)

    return image_urls


def save_images(target_folder, search_term, url, counter):
    try:
        image_content = requests.get(url).content
    except Exception as e:
        print(f"Could not download {url}- {e}")

    try:
        f = open(os.path.join(target_folder, search_term +
                              '_' + str(counter) + '.jpg'), 'wb')
        f.write(image_content)
        f.close()
        print(f'SUCCESS- saved {counter}: {url}')
    except Exception as e:
        print(f"ERROR - Could not save {url}- {e}")


def search_and_download(search_term: str, driver_path: str, target_path="./images", n_images=10):
    target_folder = os.path.join(
        target_path, "_".join(search_term.lower().split()))

    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    with webdriver.Chrome(executable_path=driver_path) as wd:
        result = fetch_image_urls(
            search_term, n_images, web_driver=wd, sleep_between_interactions=0.5)

    for index, url in enumerate(result):
        save_images(target_folder, search_term, url, index+1)


DRIVER_PATH = './chromedriver.exe'
search_term = 'among us'
number_of_images = 200
if __name__ == '__main__':
    search_and_download(search_term, DRIVER_PATH, n_images=number_of_images)
