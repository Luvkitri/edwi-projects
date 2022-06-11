from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


def send_form():
    options = webdriver.ChromeOptions()
    options.add_argument("headless")

    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    driver.get("http://127.0.0.1:5000")

    form_button = driver.find_element(By.TAG_NAME, "input")
    form_button.click()

    email_input = driver.find_element(By.ID, "email")
    name_input = driver.find_element(By.ID, "name")
    password_input = driver.find_element(By.ID, "password")
    password_repeat_input = driver.find_element(By.ID, "password-repeat")

    name_label = driver.find_element(By.XPATH, "//form/div/p[3]/b")
    name_paragraph = driver.find_element(By.XPATH, "//form/div/p[3]")
    name = name_paragraph.text.replace(name_label.text + ": ", "").strip()

    email_label = driver.find_element(By.XPATH, "//form/div/p[4]/b")
    email_paragraph = driver.find_element(By.XPATH, "//form/div/p[4]")
    email = email_paragraph.text.replace(email_label.text + ": ", "").strip()

    password_label = driver.find_element(By.XPATH, "//form/div/p[5]/b")
    password_paragraph = driver.find_element(By.XPATH, "//form/div/p[5]")
    password = password_paragraph.text.replace(password_label.text + ": ", "").strip()

    email_input.send_keys(email)
    name_input.send_keys(name)
    password_input.send_keys(password)
    password_repeat_input.send_keys(password)

    answer_select = driver.find_element(By.ID, "answer")
    options = answer_select.find_elements(By.TAG_NAME, "option")

    for option in options:
        if option.get_attribute("value") == "correct":
            option.click()
            break

    submit_button = driver.find_element(By.TAG_NAME, "button")
    submit_button.click()
    
    html_element = driver.find_element(By.XPATH, "/html")
    html_text = html_element.text
    success = False
    
    if html_text.split(' ')[0] == "Poprawnie":
        success = True
    
    print(html_text)
    print(f"Success: {success}")
    
