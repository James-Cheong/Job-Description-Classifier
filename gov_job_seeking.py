from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import pandas as pd
import time
from translate_text import translate_text


def main():
    start_time = time.time()
    # keep track of the number of marketing_box currently checking
    BOX_NUMBER = 0
    # store all jobs
    data = []
    driver = driver_init('https://www.dsal.gov.mo/jobseeking/app/#/service')
    while BOX_NUMBER <= 6:
        print(f'Searching market {BOX_NUMBER+1}...')
        # search 電腦技術員
        computer_technician = search_jobs(driver, BOX_NUMBER, '電腦技術員')
        data += computer_technician
        # search 休閒企業配對會的含有資訊科技的job
        casino_jobs = search_jobs(driver, BOX_NUMBER, '休閒企業配對會', '資訊科技')
        data += casino_jobs
        BOX_NUMBER += 1

    # store in csv
    df = pd.DataFrame(data, columns=['公司類型', '招聘職位', '薪金', '公司名稱', '學歷', '經驗/技能', '工作地點', '工作時間', '職責'])
    df.fillna('',inplace=True)
    df.iloc[:,[5,8]] = df.iloc[:,[5,8]].applymap(lambda x: translate_text('en',x))
    df.to_csv('gov_jobs.csv', index=False, encoding='utf_8_sig')
    # Close the web browser  
    driver.quit()
    end_time = time.time()
    print(f'Finished in {end_time-start_time:.2f}s')


def driver_init(url: str):
    # Set the path to the Firefox webdriver
    firefox_driver_path = "driver\geckodriver.exe"
    firefox_options = webdriver.FirefoxOptions()
    firefox_options.headless = True
    # Open the Firefox web browser
    service = Service(executable_path=firefox_driver_path)
    driver = webdriver.Firefox(service=service, options=firefox_options)
    # Navigate to the website
    driver.get(url)
    # Wait for the page to load
    driver.implicitly_wait(5)
    return driver


def load_marketing_boxes(driver, count: int):
    # find all the markets
    marketing_boxes = driver.find_elements(By.CSS_SELECTOR, ".marketing__box")
    driver.execute_script("arguments[0].scrollIntoView();", marketing_boxes[count])
    # Click on each div
    marketing_boxes[count].click()
    # Wait for the page to load
    time.sleep(0.5)


def into_job_detal_page(driver, keyword: str):
    keyword_found = False
    try:
        # search the text of minor__box equals to the keyword
        minor_divs = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".minor__box")))
        for minor_div in minor_divs:
            first_line_div = minor_div.find_element(By.CSS_SELECTOR, ".first__line")
            if first_line_div.text == keyword:
                # click into the job detail page
                driver.execute_script("arguments[0].scrollIntoView(); arguments[0].click();", first_line_div)
                keyword_found = True
                break
    except Exception as e:
        print(f'An error occurred: {e}')
    finally:
        return keyword_found


def expand_all_jobs_in_job_detail(driver):
    # get the total nums of the jobs in this page
    job_list = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div[1]/div[1]/div/div[2]/p'))).text
    job_nums = re.findall(r'\d+', job_list)[0]
    # scroll to the bottom of the page
    while len(driver.find_elements(By.CSS_SELECTOR, "div.job__box")) < int(job_nums):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
       # time.sleep(0.5)
    # expand all job_box
    action_divs = driver.find_elements(By.CSS_SELECTOR, ".action__text")
    for div in action_divs:
        # Scroll the div into view and click on it
        driver.execute_script("arguments[0].scrollIntoView(); arguments[0].click();", div)


def get_all_jobs_in_page(driver, search_str: str = None):
    all_jobs = []
    job_boxes = driver.find_elements(By.CSS_SELECTOR, "div.job__box")
    # Iterate over the job__box
    for job_box in job_boxes:
        job_in_job_box = []
        is_contain_seach_str = False
        # Iterate over the m-cell divs
        for m_cell in job_box.find_elements(By.CSS_SELECTOR, ".m-cell"):
            # Find the m-cell__title div
            m_cell_title = m_cell.find_element(By.CSS_SELECTOR, ".m-cell__title").text
            # Check if the m-cell__title text is equal to the desired value
            if m_cell_title not in ("", "空缺編號"):
                # Find the m-cell__value div
                m_cell_value = m_cell.find_element(By.CSS_SELECTOR, ".m-cell__value").text
                if search_str is not None and search_str in m_cell_value:
                    is_contain_seach_str = True
                # append all description to a list
                job_in_job_box.append(m_cell_value)
        if search_str is None or is_contain_seach_str:
            all_jobs.append(job_in_job_box)
    return all_jobs


def search_jobs(driver, count: int, keyword: str, search_str: str = None):
    load_marketing_boxes(driver, count)
    keyword_found = into_job_detal_page(driver, keyword)
    if keyword_found:
        expand_all_jobs_in_job_detail(driver)
        all_jobs = get_all_jobs_in_page(driver, search_str)
        driver.back()
        driver.refresh()
        driver.implicitly_wait(10)
        return all_jobs
    driver.refresh()
    driver.implicitly_wait(10)
    return []


if __name__ == '__main__':
    main()

