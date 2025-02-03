from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from bs4 import BeautifulSoup

import time
import re
import random
import requests
import logging
import sys

logging.basicConfig(filename="scrapper.log", level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
logging.info("----- Started scrapping -----")

fname = "google_scholar_profile.json"
dump = False

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")  # Run in headless mode (optional)
chrome_options.add_argument("--disable-gpu")  # Disable GPU rendering (optional)
driver = webdriver.Chrome(options=chrome_options)

# Google Scholar profile URL (replace YOUR_USER_ID with your ID)
gs_profile_url = "https://scholar.google.com/citations?user=7cOu9sAAAAAJ&hl=en"

# Google Scholar citation base link
abuse_exception = "1&google_abuse=GOOGLE_ABUSE_EXEMPTION%3DID%3D3c1af3a1f6ab162e:TM%3D1738604233:C%3Dr:IP%3D128.235.13.38-:S%3DKT-24sKKwdaS_tciwWnVCzo%3B+path%3D/%3B+domain%3Dgoogle.com%3B+expires%3DMon,+03-Feb-2025+22:37:13+GMT"
abuse_exception = "1"
gs_citation_url = lambda start_pos, cite : f"https://scholar.google.com/scholar?start={start_pos}&hl=en&num=10&as_sdt=80000005&sciodt=0,23&cites={cite}&scipsc=" + abuse_exception

try:
    driver.get(gs_profile_url)
    wait = WebDriverWait(driver, 5)

    show_more_button = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "#gsc_bpf_more .gs_wr"))
    )
    show_more_button.click()
    time.sleep(5)

    titles = []
    citations = []
    citations_ref = []
    citations_info = []

    article_col = driver.find_elements(By.CSS_SELECTOR, "#gsc_a_b .gsc_a_t")
    for row in article_col:
        title = row.find_element(By.CSS_SELECTOR, ".gsc_a_at")
        titles.append(title.text)

    citation_col = driver.find_elements(By.CSS_SELECTOR, "#gsc_a_b .gsc_a_c")
    for row in citation_col:
        try:
            citation = row.find_element(By.CSS_SELECTOR, ".gsc_a_ac")
            count = int(citation.text)
            url = citation.get_attribute("href")
            ref_num = re.search(r"cites=([^&]+)", url).group(1)
        except Exception:
            count = 0
            ref_num = ""
        citations.append(count)
        citations_ref.append(ref_num)

    df = pd.DataFrame({"title": titles, "citation_count": citations, "citation_ref": citations_ref})

    for i, row in df.iterrows():
        cite_count = row["citation_count"]
        cite_ref = row["citation_ref"]
        logging.info(f"User article = '{row['title']}'; citations = {cite_count}")
        if cite_count > 0:
            start_pos_list = list(range(0, cite_count, 10))
            for pos in start_pos_list:
                citation_url = gs_citation_url(pos, cite_ref)
                response = requests.get(citation_url)
                time.sleep(random.uniform(10, 60))
                if response.status_code == 200:
                    logging.info(f"fetching contents from '{citation_url}'")
                    article_map = {}
                    soup = BeautifulSoup(response.content, "html.parser")
                    articles_info = soup.find_all("div", class_="gs_a")
                    articles_title = soup.find_all("h3", class_="gs_rt")
                    assert len(articles_title) == len(articles_info)
                    for info, title in zip(articles_info, articles_title):
                        if title.a:
                            article_map = {"title":title.a.text, "url":title.a["href"], "info":info.text}
                        else:
                            article_map = {"title":title.text, "url":None, "info":info.text}
                            logging.error(f"unable to fetch title of article from '{title.text}'")
                    citations_info.append(article_map)
                else:
                    logging.error(f"status_code = {response.status_code}; unable to fetch from '{citation_url}'")
                    dump = True
                    break
            else:
                continue
            break
        else:
            citations_info.append(None)
        time.sleep(5)

    driver.quit()

    diff = len(df) - len(citations_info)
    if diff > 0:
        citations_info.extend([None] * diff)
    df['citations_info'] = citations_info
    df.to_json(fname, orient="records", lines=True)
    logging.info(f"----- dumping current results into {fname} -----") if dump else logging.info(f"----- scrapping completed, results exported to '{fname}' -----")
except Exception as e:
    logging.error(e)
    raise(e)


#TODO everything at a streatch is not possible breakdown scrapping citations per article into seperate dataframe and save seperately.
#TODO try zotero to export citations
#TODO look for already available APIs and Libraries (https://pypi.org/project/scholarly/) (https://serpapi.com/google-scholar-api)

