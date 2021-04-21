import time
from os import system
from selenium import webdriver
from plyer import notification
import argparse
import urllib
from datetime import datetime


def print_with_time(text, end_with_new_line=True):
    line = datetime.now().strftime("[%d/%m %H:%M:%S] {}").format(text)

    if end_with_new_line:
        print(line)
    else:
        print(line, end='')


valid_states = ['rj', 'sp', 'mg', 'pr', 'rs', 'sc', 'es', 'ba', 'pe', 'df', 'ce', 'ms',
                'go', 'am', 'rn', 'pb', 'pa', 'mt', 'al', 'se', 'ma', 'ac', 'ro', 'to', 'pi', 'ap', 'rr']

# Arguments handling
parser = argparse.ArgumentParser(
    description='Bot de monitoramento de anúncios da OLX')
parser.add_argument('--state', dest='state', type=str,
                    required=True, help='Nome do estado abreviado, Ex: rn')
parser.add_argument('--query', dest='query', type=str, required=True,
                    help='Pesquisa a ser feita na OLX, Ex: Galaxy S9')
parser.add_argument('--ref', dest='ref', type=int, default=60,
                    help='Número de segundos de espera entre atualizações, Ex: 60')

args = parser.parse_args()

if args.state not in valid_states:
    print_with_time(
        "Estado informado inválido, por favor, use um dos estados a baixo:")

    for state in valid_states:
        print_with_time(state)

    exit()

# Selenium
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-crash-reporter")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-in-process-stack-traces")
chrome_options.add_argument("--disable-logging")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--log-level=3")
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--ignore-ssl-errors')
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

browser = webdriver.Chrome("./chromedriver.exe", options=chrome_options)

url = "https://{}.olx.com.br/?q={}&sf=1".format(args.state,
                                                urllib.parse.quote(args.query))

browser.get(url)

# Fill ad_list before checking new ads
old_ad_list = {}


def fill_ad_list():
    ul_list = browser.find_element_by_id("ad-list")
    ads = ul_list.find_elements_by_tag_name("li")

    for ad in ads:
        try:
            ad_a = ad.find_element_by_tag_name(
                "a")

            ad_title = ad_a.get_attribute("title")
            ad_id = ad_a.get_attribute("data-lurker_list_id")
            ad_href = ad_a.get_attribute("href")

            old_ad_list[ad_id] = {"id": ad_id,
                                  "title": ad_title, "href": ad_href}
        except:
            continue


fill_ad_list()
print_with_time(
    "Bot rodando! Automaticamente será verificado novos anúncios na url: {}".format(url))

notification.notify(
    title="Bot OLX rodando!",
    message="Agora só esperar aparecer novo anúncios automaticamente!",
    timeout=10
)

# Checking for new ads
while True:
    time.sleep(args.ref)
    print_with_time("Procurando por novos anúncios...\r", False)
    browser.refresh()

    ul_list = browser.find_element_by_id("ad-list")
    ads = ul_list.find_elements_by_tag_name("li")

    new_ad_list = {}

    found_new_ad = False
    for ad in ads[:5]:
        try:
            ad_a = ad.find_element_by_tag_name(
                "a")

            ad_title = ad_a.get_attribute("title")
            ad_id = ad_a.get_attribute("data-lurker_list_id")
            ad_href = ad_a.get_attribute("href")

            if ad_id not in old_ad_list:
                found_new_ad = True
                print_with_time(
                    "Novo anúncio encontrado!         \nTítulo: {}\nLink: {}".format(ad_title, ad_href))

                notification.notify(
                    title="Um novo anúncio foi encontrado!",
                    message=ad_title,
                    timeout=10
                )

                system("chrome {}".format(ad_href))

            new_ad_list[ad_id] = {"id": ad_id,
                                  "title": ad_title, "href": ad_href}
        except:
            continue

    if not found_new_ad:
        print_with_time("Nenhum anúncio novo encontrado.  \r", False)
    else:
        old_ad_list = new_ad_list.copy()
