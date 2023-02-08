from gov_job_seeking import driver_init
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import threading


# job_detail = []
# start_time=time.time()
# for i in range(1, 6):
#     driver = driver_init(
#         f'https://jobsearch.hello-jobs.com/Job-Search/%E8%B3%87%E8%A8%8A%E7%A7%91%E6%8A%80%E5%8F%8A%E9%9B%BB%E5%AD%90%E9%80%9A%E8%A8%8A-Functional-Area-Jobs-in-Macau/F29.aspx?pageNumber={i}')
#     driver.implicitly_wait(10)
#     # get all the jobs in current page
#     links = driver.find_elements(By.CSS_SELECTOR, "a[id$='_lnkJobTitle']")

#     for i in range(len(links)):
#         links = driver.find_elements(By.CSS_SELECTOR, "a[id$='_lnkJobTitle']")
#         links[i].click()
#         job_title = driver.find_element(By.ID, 'ctl00_MasterContentPlaceHolder_GeneralJobDescription_LblJobTitle').text
#         job_description = driver.find_elements(By.CLASS_NAME, 'RMdescription')[-1].text
#         company_name = driver.find_element(By.ID, 'ctl00_MasterContentPlaceHolder_GeneralJobDescription_lblCompanyDisplayName').text
#         industry = driver.find_element(By.ID, 'ctl00_MasterContentPlaceHolder_GeneralJobDescription_LblReqIndustry').text
#         row = {'招聘職位': job_title, '職責': job_description, '公司名稱': company_name, '公司類型': industry}
#         job_detail.append(row)
#         driver.back()
#         time.sleep(2)
#     driver.quit()
# df = pd.DataFrame(job_detail)
# df.to_csv('hello_jobs.csv', index=False, encoding='utf_8_sig')
# end_time=time.time()
# print(f'used {end_time-start_time} s')

job_detail = []
lock = threading.Lock()


def scrape_page(page_num):
    driver = driver_init(
        f'https://jobsearch.hello-jobs.com/Job-Search/%E8%B3%87%E8%A8%8A%E7%A7%91%E6%8A%80%E5%8F%8A%E9%9B%BB%E5%AD%90%E9%80%9A%E8%A8%8A-Functional-Area-Jobs-in-Macau/F29.aspx?pageNumber={page_num}')
    driver.implicitly_wait(10)
    links = driver.find_elements(By.CSS_SELECTOR, "a[id$='_lnkJobTitle']")
    for i in range(len(links)):
        links = driver.find_elements(By.CSS_SELECTOR, "a[id$='_lnkJobTitle']")
        links[i].click()
        job_title = driver.find_element(By.ID, 'ctl00_MasterContentPlaceHolder_GeneralJobDescription_LblJobTitle').text
        job_description = driver.find_elements(By.CLASS_NAME, 'RMdescription')[-1].text
        company_name = driver.find_element(By.ID, 'ctl00_MasterContentPlaceHolder_GeneralJobDescription_lblCompanyDisplayName').text
        industry = driver.find_element(By.ID, 'ctl00_MasterContentPlaceHolder_GeneralJobDescription_LblReqIndustry').text
        post_date = driver.find_element(By.ID, 'ctl00_MasterContentPlaceHolder_GeneralJobDescription_LblJobPostingDate').text
        row = {'招聘職位': job_title, '職責': job_description, '公司名稱': company_name, '公司類型': industry, '張貼日期': post_date}
        with lock:
            job_detail.append(row)
        driver.back()
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "ctl00_Body")))
    driver.quit()
    return pd.DataFrame(job_detail)


if __name__ == '__main__':
    start_time = time.time()
    threads = []
    for i in range(1, 6):
        t = threading.Thread(target=scrape_page, args=(i,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()
    df = pd.DataFrame(job_detail)
    df.to_csv('hello_jobs.csv', index=False, encoding='utf_8_sig')
    end_time = time.time()
    print(f'used {end_time-start_time} s')
