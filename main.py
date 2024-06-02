import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import json
import glob
import shutil
from PyPDF2 import PdfFileMerger

settings = {
    "recentDestinations": [{
        "id": "Save as PDF",
        "origin": "local",
        "account": "",
    }],
    "selectedDestinationId": "Save as PDF",
    "version": 2
}

foldername = ""
downloadPath = ""
f = open(r"./input.txt", "r")

for i_link in f:
    foldername = i_link.split(".")[1]
    downloadPath = r"./" + foldername + "//"
    if os.path.exists(downloadPath):
        shutil.rmtree(downloadPath)
    if os.path.exists(downloadPath) == False:
        os.mkdir(downloadPath)

    prefs = {'printing.print_preview_sticky_settings.appState': json.dumps(settings),
             'download': {
                 'default_directory':downloadPath,
                 "directory_upgrade": True,
                 "extensions_to_open": ""
             },
             "savefile.default_directory": downloadPath,
             'directory_upgrade': True,
             "safebrowsing.enabled": True
             }
    s = Service(ChromeDriverManager().install())
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    chrome_options.add_argument('--incognito')
    chrome_options.add_experimental_option('prefs', prefs)
    chrome_options.add_argument('--kiosk-printing')

    browser = webdriver.Chrome(service=s, options = chrome_options)
    browser.maximize_window()
    browser.get(i_link)

    a_elements = browser.find_elements(By.TAG_NAME, "a")
    href_links = []
    uniq_hrefs = []
    final_uniq_hrefs = []

    for link in a_elements:
        href_links.append(link.get_attribute('href'))
    [uniq_hrefs.append(x) for x in href_links if x not in uniq_hrefs]

    for uniq_href in uniq_hrefs:
        if uniq_href !=None and foldername.lower() in uniq_href.lower():
            if uniq_href[0:3] == "tel":
                continue
            if uniq_href[0:4] == "mail":
                continue
            if uniq_href[0:4] == "":
                continue
            if "linkedin" in uniq_href:
                continue
            if "information".lower() in uniq_href.lower():
                continue
            if "main-content".lower() in uniq_href.lower():
                continue
            final_uniq_hrefs.append(uniq_href)

    if len(final_uniq_hrefs) <= 15:
        pass
    else:
        final_uniq_hrefs = final_uniq_hrefs[:15]

    for final_uniq_href in final_uniq_hrefs:
        print(final_uniq_href)
        browser.get(final_uniq_href)
        browser.execute_script('window.print();')
        time.sleep(5)

    files = list(filter(os.path.isfile, glob.glob(downloadPath + "*.pdf")))
    files.sort(key=lambda x: os.path.getmtime(x))

    merger = PdfFileMerger()
    for pdf in files:
        merger.append(open(pdf, 'rb'))

    with open(downloadPath + "//" + "consolidated" + ".pdf", "wb") as singlefile:
        merger.write(singlefile)
    browser.close()
f.close()