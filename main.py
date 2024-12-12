import time
import initialize
import json
import re
import base64
import os
import random

failed_OCR_limit = 3  # 当自动识别验证码出错超过该值，切换为手动输入
Debug = True  # Open the browser interface


def check_imports() -> int:
    try:
        import ddddocr
        import selenium
        import fake_useragent
    except ImportError:
        libs = ["selenium", "fake_useragent", "ddddocr"]
        print("警告:你似乎还没有安装完全这些依赖项:\n" + "\n".join(libs))
        if (input("输入y以自动安装:") == "y"):
            for i in libs:
                os.system(
                    "pip install -i https://pypi.tuna.tsinghua.edu.cn/simple " + i)
                print(i, "安装完成！")
            return 0
        else:
            print("缺少必要依赖项")
            print("程序无法运行，即将退出")
            input("Press Enter to Continue...")
            return -1

    print("所有依赖库已安装")
    return 0


URL_LOGIN = "http://id.scu.edu.cn/enduser/sp/sso/scdxplugin_jwt23?enterpriseId=scdx&target_url=index"
URL_SELECT_COURSE = "http://zhjw.scu.edu.cn/student/courseSelect/courseSelect/index"
URL_PLAN_COURSE = "http://zhjw.scu.edu.cn/student/courseSelect/planCourse/index"
URL_FREE_COURSE = "http://zhjw.scu.edu.cn/student/courseSelect/freeCourse/index"


# load setting
setting = {"manual_login": False}
try:
    with open("setting.json", encoding="utf-8") as f:
        setting_load = json.load(f)
        setting_load["manual_login"]
        setting = setting_load
except FileNotFoundError:
    with open("setting.json", "w", encoding="utf-8") as f:
        json.dump(setting, f, indent=2)

# load user data
user_data = {}
try:
    with open("user_data.json", mode="r", encoding="utf-8") as file:
        user_data: dict = json.load(file)
        # try to access,if it not exist,this will raise a exception
        user_data["std_id"]
        user_data["password"]
        user_data["course"]
except FileNotFoundError:
    print("你似乎还没有在本地保存账户信息，请手动输入")
    user_data = initialize.main()


def manual_login():
    print("手动登录")
    url = "http://zhjw.scu.edu.cn/login"
    driver.get(url)


def auto_login():
    print("正在登录...")
    # login the SCU Dean's Office
    driver.get(URL_LOGIN)

    std_id_box = driver.find_element(
        By.XPATH, "//*[@id=\"app\"]/div[1]/div/div[2]/div/div[1]/div[2]/div[2]/div/form/div[1]/div/div/div[2]/div/input")
    password_box = driver.find_element(
        By.XPATH, "//*[@id=\"app\"]/div[1]/div/div[2]/div/div[1]/div[2]/div[2]/div/form/div[2]/div/div/div[2]/div/input")
    captcha_box = driver.find_element(
        By.XPATH, "//*[@id=\"app\"]/div[1]/div/div[2]/div/div[1]/div[2]/div[2]/div/form/div[3]/div/div/div/div/input")
    login_button = driver.find_element(
        By.XPATH, "//*[@id=\"app\"]/div[1]/div/div[2]/div/div[1]/div[2]/div[2]/div/form/div[4]/div/button")
    # the following varible has 3 types "id","passwd","captcha"
    error_type = ""

    captcha_solver = ddddocr.DdddOcr(beta=True, show_ad=False)
    captcha_pic_path = os.getcwd()+"\\captcha.jpg"
    failed_OCR_times = 0

    while True:
        time.sleep(0.1)
        if error_type == "id":
            user_data["std_id"] = input("请再次输入你的账户ID: ")
            initialize.save_user_date(user_data)
            error_type = ""
        std_id_box.send_keys(user_data["std_id"])
        if error_type == "passwd":
            user_data["password"] = input("请再次输入你的密码: ")
            initialize.save_user_date(user_data)
            error_type = ""
        password_box.send_keys(user_data["password"])

        # captcha will update automatically,so it should be updated each time.
        captcha_base64 = driver.find_element(
            By.XPATH, "//*[@id=\"app\"]/div[1]/div/div[2]/div/div[1]/div[2]/div[2]/div/form/div[3]/div/div/img").get_attribute("src")
        captcha_img = base64.b64decode(
            captcha_base64[captcha_base64.find("base64")+7:])
        if failed_OCR_times <= failed_OCR_limit:
            if failed_OCR_times:
                print("目前自动验证失败次数:", failed_OCR_times)
            print("下方是OCR库的输出")
            captcha_text = captcha_solver.classification(captcha_img)
            print("自动识别到验证码：", captcha_text)
        else:  # enter CAPTCHA manully
            with open("captcha.jpg", mode="wb") as file:
                file.write(captcha_img)
            os.system("explorer "+captcha_pic_path)
            captcha_text = input("自动识别验证码失败次数已过多，请手动输入: ")

        if error_type == "captcha":
            failed_OCR_times += 1
            captcha_box.send_keys(captcha_text)
            error_type = ""
        else:
            captcha_box.send_keys(captcha_text)
        login_button.click()
        time.sleep(1)
        catch_error = driver.find_element(
            By.XPATH, "/html/body/div[2]").get_attribute("innerHTML")
        error_msg = re.search(r"(?<=<span>).*(?=</span>)", catch_error)
        if not error_msg:
            print("登录成功！")
            print("Loading the index page...")
            break
        else:
            message = error_msg.group()
            print("Please try again")
            print("Error message:", message)
            if "验证码" in message or "verification" in message:
                error_type = "captcha"
            elif "用户名或密码" in message:
                error_type = "id"
            elif "锁定" in message:
                error_type = "passwd"
            else:
                error_type = ""
            std_id_box.clear()
            password_box.clear()
            captcha_box.clear()


def catch_course(c_type: str):
    if (len(user_data["course"][c_type]) == 0):
        return
    type_name = {"a": "Plan courses", "b": "Free courses"}
    if c_type == "a":
        driver.find_element(By.XPATH, "//*[@id=\"faxk\"]").click()
    elif c_type == "b":
        driver.find_element(By.XPATH, "//*[@id=\"zyxk\"]").click()
    else:
        raise TypeError("No such type "+c_type)
    wait_for_ready(web_wait)

    wait_for_ready(web_wait)
    for course in user_data["course"][c_type]:
        driver.switch_to.frame('ifra')
        course_id_box = driver.find_element(By.XPATH, "//*[@id=\"kch\"]")
        search_box = driver.find_element(
            By.XPATH, "//*[@id=\"queryButton\"]")
        course_id, course_index = course["course_id"], course["course_index"]
        course_id_box.clear()
        course_id_box.send_keys(course_id)
        search_box.click()
        wait_for_ready(web_wait)
        time.sleep(0.1)

        web_wait.until(lambda driver: driver.execute_script(
            "return document.getElementById(\"queryButton\").innerText.indexOf(\"正在\")==-1") == True)
        driver.switch_to.default_content()
        web_wait.until(lambda driver: driver.execute_script(
            "return document.getElementById('ifra')==null") == False)
        time.sleep(0.1)
        find_target = driver.execute_script(
            select_course_js, "%s_%s" % (course_id, course_index)) == "yes"
        # logs = driver.get_log("browser")
        # for log in logs:
        #     print(log)
        if find_target:
            print("Successfully picked up the course with ID %s_%s" %
                  (course_id, course_index))

            submit_box = driver.find_element(
                By.XPATH, "//*[@id=\"submitButton\"]")
            submit_box.click()
        else:
            print("Failed to find the course with ID %s_%s" %
                  (course_id, course_index))
    time.sleep(random.random()*2)
    # submit the choices,then return the information and delete the courses that are done


def check_result(type_name, c_type):
    wait_for_ready(web_wait)
    web_wait.until(lambda driver: driver.execute_script(
        "return document.getElementsByClassName(\"header smaller lighter grey\")[0].innerText.indexOf(\"结果\")!=-1") == True)
    print("Here are the results for %s:" % (type_name[c_type]))
    time.sleep(0.3)
    results = json.loads(driver.execute_script(check_result_js))
    """
        the result is a json object
        [
            {
                "subject":"计算机导论(114514_01)",
                "result":false,//this is a bool value
                "detail":"你已选择此课程"
            },
            ....
        ]
        """
    for result in results:
        if result["result"]:
            print("Successfully catched the course(%s)" %
                  (result["subject"]))
            numbers = re.findall(r"\d+", result["subject"])
            user_data["course"][c_type].remove(
                {"course_id": numbers[0], "course_index": numbers[1]})
            print("Delete this course from the user_data")
        else:
            if Debug:
                print("Failed to catch the course(%s)" % (
                    result["subject"]), "Failure Info:%s" % (result["detail"]))
    initialize.save_user_date(user_data)
    # time.sleep(60)


if __name__ == '__main__':
    if check_imports() != 0:
        exit()

    import ddddocr
    from selenium import webdriver
    from fake_useragent import UserAgent
    from selenium.webdriver.support.wait import WebDriverWait
    from selenium.webdriver.common.by import By

    # configure the browser
    option = webdriver.ChromeOptions()
    option.add_argument("--headless")
    option.add_argument("--incognito")
    option.add_argument("--nogpu")
    option.add_argument("--disable-gpu")
    option.add_argument("--window-size=1280,1280")
    option.add_argument("--no-sandbox")
    option.add_argument("--enable-javascript")
    option.add_experimental_option("excludeSwitches", ["enable-automation"])
    option.add_experimental_option("useAutomationExtension", False)
    option.add_argument("--disable-blink-features=AutomationControlled")
    option.add_experimental_option("excludeSwitches", ["enable-logging"])
    option.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    ua = UserAgent()
    userAgent = ua.random
    print("使用随机UA", userAgent)
    if Debug:
        driver = webdriver.Chrome()
    else:
        driver = webdriver.Chrome(options=option)

    driver.execute_cdp_cmd('Network.setUserAgentOverride',
                           {"userAgent": userAgent})
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                           "source": "Object.defineProperty(navigator,'webdriver',{get: () => undefined})"})

    driver.implicitly_wait(10)
    web_wait = WebDriverWait(driver, 30, 0.5)

    def wait_for_ready(driver_wait: WebDriverWait):
        driver_wait.until(lambda webDriver: webDriver.execute_script(
            "return document.readyState") == "complete", "Please check your Internet and rerun the program!")

    if setting["manual_login"]:
        manual_login()
    else:
        auto_login()

    # 等待登录完成后的跳转
    WebDriverWait(driver, 120, 0.5).until(lambda driver: driver.current_url == "http://zhjw.scu.edu.cn/index" or driver.current_url ==
                                          "http://zhjw.scu.edu.cn/", "Please check your Internet and rerun the program!")

    print("Redirecting to select course page")
    # go to select course page
    driver.get(URL_SELECT_COURSE)
    # make sure the page is ready
    wait_for_ready(web_wait)

    with open("javascript"+os.sep+"select_course.js") as f:
        select_course_js = f.read()
    with open("javascript"+os.sep+"check_result.js") as f:
        check_result_js = f.read()

    time.sleep(0.3)

    catch_error = driver.find_element(
        By.XPATH, "//*[@id=\"page-content-template\"]/div")

    if "非选课" in catch_error.text:
        print(catch_error.text)
        print("Please wait until the course-choosing is available...")
        exit()

    while True:
        for course_type in user_data["course"]:
            catch_course(course_type)
            if (driver.current_url != URL_SELECT_COURSE):
                driver.get(URL_SELECT_COURSE)
            wait_for_ready(web_wait)

    driver.close()
