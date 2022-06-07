from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

def send_form():
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    driver.get('http://127.0.0.1:5000')
    
    form_button = driver.find_element(By.TAG_NAME, "input")
    form_button.click()
    
    email_input = driver.find_element(By.ID, "email")
    name_input = driver.find_element(By.ID, "name")
    password_input = driver.find_element(By.ID, "password")
    password_repeat_input = driver.find_element(By.ID, "password-repeat")
    
    email_input.send_keys("eksploracja@eksploracja.kis.p.lodz.pl")
    name_input.send_keys("eksploracja")
    password_input.send_keys("tajnehaslo")
    password_repeat_input.send_keys("tajnehaslo")
    
    answer_select = driver.find_element(By.ID, "answer")
    options = answer_select.find_elements(By.TAG_NAME, "option")
    
    for option in options:
        if option.get_attribute("value") == "correct":
            option.click()
            break
        
    submit_button = driver.find_element(By.TAG_NAME, "button")
    submit_button.click()