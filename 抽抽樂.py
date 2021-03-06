# Part 1. 篩選抽抽樂連結
import requests
from bs4 import BeautifulSoup

url = "https://fuli.gamer.com.tw/index.php"
h = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36"
}
response = requests.get(url, verify=False, headers=h)
html = BeautifulSoup(response.text)

lucky_draw_links = []
items = html.find("div", class_="item-list-box").find_all("a", class_="items-card")
for item in items:
    tag = item.find("span", class_="type-tag")
    if tag.text == "抽抽樂":
        title = item.find("h2", class_="items-title").text
        href = item["href"]
        lucky_draw_links.append(href)
        print(title, "\n", href)
        print("-" * 30)

# Part 2. Selenium自動觀看廣告
import time
from selenium.webdriver import Chrome
from http.cookies import SimpleCookie
from selenium import webdriver
import selenium.webdriver.support.ui as ui
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

rawdata = input("請輸入Cookie: ")

driver = Chrome("./chromedriver")
driver.get("https://fuli.gamer.com.tw")
driver.maximize_window()

# selenium add cookies(帳密)
cookie = SimpleCookie()
cookie.load(rawdata)
cookies = {}
for key, morsel in cookie.items():
    # print(key, morsel.value)
    cookies[key] = morsel.value
    driver.add_cookie({"name": key, "value": morsel.value})

loopcount = 10
times = 0  # selenium 執行次數
while times < loopcount:
    print("迴圈", times + 1)
    for lucky_draw_link in lucky_draw_links:
        driver.get(lucky_draw_link)  # get(抽抽樂連結)

        # 本日免費兌換次數已用盡
        is_disable_element_exist = True if len(driver.find_elements_by_class_name("is-disable")) > 0 else False
        if is_disable_element_exist == True:
            obj = driver.find_elements_by_class_name("is-disable")
            print(obj[0].text, lucky_draw_link)
            if obj[0].text.__contains__("廣告能量補充中"):
                loopcount += 1
            continue

        # 看廣告免費兌換
        WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.CLASS_NAME, "c-accent-o"))).click()

        wait = ui.WebDriverWait(driver, 10)  # Python+Selenium定位不到元素常見原因及解決辦法(https://support.i-search.com.cn/article/1561452266407)
        # question-popup
        question_popup_element_exist = True if len(driver.find_elements_by_id("answer-count")) > 0 else False  # 利用"共需答對幾題?"判斷是否彈跳出勇者問答題
        if question_popup_element_exist == True:
            answer_count_split = driver.find_element_by_id("answer-count").text.split()
            answer_count = int(answer_count_split[1])  # 取題數

            questions = 0  # 執行問題(次數)
            element_id = 1
            for questions in range(answer_count):
                question_element_id = "question-" + str(element_id)
                options = wait.until(lambda driver: driver.find_element_by_id(question_element_id).find_elements_by_class_name("fuli-option"))  # options = list[0, 1, 2]
                data_answer = wait.until(lambda driver: driver.find_element_by_id(question_element_id).find_element_by_tag_name('a')).get_attribute('data-answer')  # data_answer = 'str' 3
                data_answer = int(data_answer) - 1
                options[data_answer].click()
                time.sleep(3)  # wait for the webpage to load before executing the next line of code (https://stackoverflow.com/questions/60824679/time-sleep-on-chromedriver)
                element_id += 1
                questions += 1

            # watch_ad
            watch_ad_element = wait.until(lambda driver: driver.find_element_by_id("btn-buy"))
            driver.execute_script("arguments[0].click();", watch_ad_element)  # there is another element (div below the button) will receive the click. Driver.execute_script("arguments[0].click();", element) Takes your locator (element) as first argument and perform the action of click.(https://sqa.stackexchange.com/questions/40678/using-python-selenium-not-able-to-perform-click-operation)
            time.sleep(3)

        # if_watch_ad
        try:
            if_watch_ad = wait.until(lambda driver: driver.find_element_by_class_name("btn-primary"))
            if_watch_ad.click()
        except TimeoutException:
            print("if_watch_ad: TimeoutException(無廣告)")
            pass

        # close_ad
        # print(len(driver.find_elements_by_tag_name('iframe')))
        iframe = wait.until(lambda driver: driver.find_elements_by_tag_name('iframe')[-1])  # python+selenium 自動化過程中遇到的元素不可見時間以及webelement不可見的處理方法(https://iter01.com/467737.html)
        # 有三種不同的close_ad按鈕(視廣告出現型態而定)
        driver.switch_to.frame(iframe)
        try:
            while True:
                close_element_exist = True if len(driver.find_elements_by_id("close_button_icon")) > 0 else False
                if close_element_exist == True:
                    print("close_element_exist:", close_element_exist)
                    WebDriverWait(driver, 60).until(EC.invisibility_of_element_located((By.ID, "count_down")))  # visibility: hidden 0 秒後可獲得獎勵(https://www.itread01.com/content/1547684126.html)
                    WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.ID, "close_button_icon"))).click()
                    break

                dismiss_button_element_exist = True if len(driver.find_elements_by_id("dismiss-button-element")) > 0 else False
                if dismiss_button_element_exist == True:
                    print("dismiss_button_element_exist:", dismiss_button_element_exist)
                    WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.ID, "dismiss-button-element"))).click()
                    break

                close_circle_element_exist = True if len(driver.find_elements_by_xpath('//*[@id="google-rewarded-video"]/img[3]')) > 0 else False
                if close_circle_element_exist == True:
                    print("close_circle_element_exist:", close_circle_element_exist)
                    # Video will play with sound
                    while True:
                        rewardResumebutton_1_element_exist = True if len(driver.find_elements_by_xpath('//*[@id="google-rewarded-video"]/div[3]/div[7]/div/div[3]/div[2]'))> 0 else False
                        if rewardResumebutton_1_element_exist == True:
                            print("rewardResumebutton_1_element_exist:", rewardResumebutton_1_element_exist)
                            WebDriverWait(driver, 6).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="google-rewarded-video"]/div[3]/div[7]/div/div[3]/div[2]'))).click()
                            break
                        rewardResumebutton_2_element_exist = True if len(driver.find_elements_by_xpath('// *[ @ id = "google-rewarded-video"] / div[3] / div[5] / div / div[3] / div[2]')) > 0 else False
                        if rewardResumebutton_2_element_exist == True:
                            print("rewardResumebutton_2_element_exist:", rewardResumebutton_2_element_exist)
                            WebDriverWait(driver, 6).until(EC.element_to_be_clickable((By.XPATH, '// *[ @ id = "google-rewarded-video"] / div[3] / div[5] / div / div[3] / div[2]'))).click()
                            break
                        break
                    WebDriverWait(driver, 60).until(EC.text_to_be_present_in_element((By.CLASS_NAME, "rewardedAdUiAttribution"), "Reward in 1 seconds"))
                    time.sleep(3)  # 播放結束
                    WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="google-rewarded-video"]/img[3]'))).click()
                    break
                break

        except TimeoutException:
            # 已移除廣告。(這個廣告使用了太多裝置資源，因此 Chrome 已將其移除。)
            main_message_element_exist = True if len(driver.find_elements_by_id("main-message")) > 0 else False
            if main_message_element_exist == True:
                print("main_message_element_exist(已移除廣告):", main_message_element_exist, ":", lucky_draw_link)
                driver.refresh()
                time.sleep(3)
            loopcount += 1
            print("loopcount += 1")
            continue

        # agree_confirm
        driver.switch_to.default_content()
        time.sleep(5)  # 等待換頁

        # 發生錯誤，請重新嘗試(1) 或  廣告能量補充中 請稍後再試
        btn_danger_element_exist = True if len(driver.find_elements_by_class_name("btn-danger")) > 0 else False
        if btn_danger_element_exist == True:
            print("btn_danger_element_exist(發生錯誤):", btn_danger_element_exist, ":", lucky_draw_link)
            driver.find_element_by_class_name("btn-danger").click()
            driver.refresh()
            loopcount += 1
            continue

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # Selenium Page down(https://stackoverflow.com/questions/20986631/how-can-i-scroll-a-web-page-using-selenium-webdriver-in-python)
        agree_confirm = driver.find_element_by_css_selector('#buyD > div.flex-center.agree-confirm > div > label')
        action = ActionChains(driver)
        time.sleep(3)  # 滾動至頁底
        action.move_to_element(agree_confirm).click().perform()  # 滑鼠移動到"我已閱讀注意事項，並確認兌換此商品"<label> Tag元素點擊打勾(https://stackoverflow.com/questions/40170915/why-actionchainsdriver-move-to-elementelem-click-perform-twice)
        time.sleep(3)  # 觀察打勾
        WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.CLASS_NAME, "c-primary"))).click()

        # 您尚未勾選「我已閱讀注意事項，並確認兌換此商品」
        btn_danger_element_exist = True if len(driver.find_elements_by_class_name("btn-danger")) > 0 else False
        while btn_danger_element_exist == True:
            print("您尚未勾選「我已閱讀注意事項，並確認兌換此商品」")
            driver.find_element_by_class_name("btn-danger").click()
            action.move_to_element(agree_confirm).click().perform()  # 滑鼠移動到"我已閱讀注意事項，並確認兌換此商品"<label> Tag元素點擊打勾
            time.sleep(3)  # 觀察打勾
            driver.find_element_by_class_name("c-primary").click()  # 確定兌換
            btn_danger_element_exist = True if len(driver.find_elements_by_class_name("btn-danger")) > 0 else False
            if btn_danger_element_exist == False:
                break
            else:
                continue

        submit = wait.until(lambda driver: driver.find_element_by_class_name("btn-primary"))  # 您確定要兌換此商品嗎？
        submit.click()
    times += 1
    time.sleep(240) #廣告能量補充中
driver.quit()
