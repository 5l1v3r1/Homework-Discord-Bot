import glob
import time

import discord
from discord import File
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

accepcted_courses = ['10th Grade Algebra II Pre-AP (Stuckey) Work', '10th Grade - Pre AP Chemistry Work',
                     '10th Grade English II Pre-AP (Keeling) Work', '10th Grade World History AP (Jacobie) Work']
pictures = ['https://img.icons8.com/cotton/2x/test-tube.png',
            'https://cdn2.iconfinder.com/data/icons/circle-icons-1/64/calculator-512.png',
            'https://img.pngio.com/english-icon-png-212470-free-icons-library-english-subject-png-2246_2246.jpg',
            'https://cdn4.iconfinder.com/data/icons/education-254/64/global-earth-worldwide-geography-planet-Maps-history-512.png']


def wait_for_element(driver, xpath):
    try:
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, xpath)))
        return True
    except TimeoutException:
        print("Loading took too much time!")
        return False


async def send_msg(ctx, msg):
    print(msg)
    await ctx.send(msg)


async def send_assignment_embed(ctx, class_name, assignments):
    embed = discord.Embed(title=f"{class_name} Work", description=f"{len(assignments)} Assignments", color=0xff0000)
    if class_name.find("Chemistry") != -1:
        url = pictures[0]
    elif class_name.find("Algebra") != -1:
        url = pictures[1]
    elif class_name.find("English") != -1:
        url = pictures[2]
    elif class_name.find("History") != -1:
        url = pictures[3]

    embed.set_thumbnail(
        url=url)
    for asng in assignments:
        if asng.text.find("Forum") != -1:
            continue
        embed.add_field(name="Assignment", value=asng.text, inline=False)
    await ctx.send(embed=embed)
    print(f"{class_name} | {assignments}")


class Moodle:
    def __init__(self, username, password):
        self.url = "https://neisd.mrooms.net/login/"
        self.username = username
        self.password = password
        self.driver = None

    def setup(self):
        chrome_options = webdriver.ChromeOptions()
        prefs = {'download.default_directory': 'C:\\Users\\nickm\\PycharmProjects\\HomeworkBot\\DOWNLOADS'}
        chrome_options.add_experimental_option('prefs', prefs)
        self.driver = webdriver.Chrome("C:\\chromedriver.exe", chrome_options=chrome_options)
        self.driver.get(self.url)

    async def login(self, ctx):
        await send_msg(ctx, "Attempting to login...")
        try:
            self.driver.get(self.url)
            wait_for_element(self.driver, "/html/body/div[3]/div/main/section/div/div[2]/div[1]/form/input[3]")
            self.driver.find_element_by_id("username").click()
            self.driver.find_element_by_id("username").send_keys(self.username)
            self.driver.find_element_by_id("password").click()
            self.driver.find_element_by_id("password").send_keys(self.password)
            self.driver.find_element_by_id("loginbtn").click()
        except Exception as e:
            await send_msg(ctx, "Error logging in")
            return False
        await send_msg(ctx, "Logged in successfully! :white_check_mark:")
        return True

    async def upload_files(self, ctx, title):
        for file in glob.glob("/DOWNLOADS"):
            ctx.send(title, file=File(file))

    async def fetch_work(self, ctx, class_=None):
        await send_msg(ctx, "Attempting to retrive work...")
        self.driver.find_element_by_css_selector(".js-snap-pm-trigger").click()
        time.sleep(1)
        a = self.driver.find_elements_by_css_selector('.coursecard-body h3 a')
        satisfied = False
        index = 0
        found_index = 0
        while index < len(a) and not satisfied:
            # get cards to each class - have to get list each time so elements arent stale
            if index == 0:
                tag = self.driver.find_elements_by_css_selector('.coursecard-body h3 a')[0]
            else:
                tag = self.driver.find_elements_by_css_selector('.coursecard-body h3 a')[index]
                self.driver.find_element_by_css_selector(".js-snap-pm-trigger").click()
                time.sleep(.5)

            if class_ is not None and tag.text.lower().find(class_.lower()) == -1:
                index += 1
                continue
            else:
                # clicks the a tag to take us to the course
                try:
                    tag.click()
                except StaleElementReferenceException:
                    tag = self.driver.find_elements_by_css_selector('.coursecard-body h3 a')[index]
                    tag.click()

                title = self.driver.find_element_by_css_selector("#page-mast h1 a").text

                if title.find("Algebra") == -1:
                    if title.find("English") == -1:
                        if title.find("History") == -1:
                            if title.find("Chemistry") == -1:
                                if class_ is None:
                                    print("hi!")
                                    index += 1
                                    self.driver.execute_script("window.history.go(-1)")
                                    time.sleep(1)
                                    continue

                if title.find("Algebra") != -1:
                    try:
                        self.driver.find_element_by_xpath(
                            "/html/body/div[4]/div/main/div[2]/div/div[2]/section/div/div/ul/li[3]/div/nav/a[2]").click()
                    except Exception:
                        self.driver.find_element_by_xpath(
                            "/html/body/div[4]/div/main/div[2]/div/div[2]/section/div/div/ul/li[3]/div/nav/a[2]").click()

                # find all assigment cards
                li_s = self.driver.find_elements_by_css_selector(
                    ".state-visible div ul .snap-activity div div div h3 a p")
                if title.find("English") != -1:
                    await send_assignment_embed(ctx, title, li_s[0:3])
                else:
                    await send_assignment_embed(ctx, title, li_s)

                # go back
                if title.find("Algebra") != -1:
                    self.driver.execute_script("window.history.go(-2)")
                else:
                    self.driver.execute_script("window.history.go(-1)")
                time.sleep(1)
                index += 1
                found_index += 1
                if class_ is not None:
                    satisfied = True

                if found_index == 4:
                    satisfied = True

    async def download_work(self, ctx, class_=None):
        await send_msg(ctx, "Attempting to download work...")
        self.driver.find_element_by_css_selector(".js-snap-pm-trigger").click()
        time.sleep(1)
        a = self.driver.find_elements_by_css_selector('.coursecard-body h3 a')
        satisfied = False
        index = 0
        found_index = 0
        while index < len(a) and not satisfied:
            # get cards to each class - have to get list each time so elements arent stale
            if index == 0:
                tag = self.driver.find_elements_by_css_selector('.coursecard-body h3 a')[0]
            else:
                tag = self.driver.find_elements_by_css_selector('.coursecard-body h3 a')[index]
                self.driver.find_element_by_css_selector(".js-snap-pm-trigger").click()
                time.sleep(.5)

            if class_ is not None and tag.text.lower().find(class_.lower()) == -1:
                index += 1
                continue
            else:
                # clicks the a tag to take us to the course
                try:
                    tag.click()
                except StaleElementReferenceException:
                    tag = self.driver.find_elements_by_css_selector('.coursecard-body h3 a')[index]
                    tag.click()

                title = self.driver.find_element_by_css_selector("#page-mast h1 a").text

                if title.find("Algebra") == -1:
                    if title.find("English") == -1:
                        if title.find("History") == -1:
                            if title.find("Chemistry") == -1:
                                if class_ is None:
                                    print("hi!")
                                    index += 1
                                    self.driver.execute_script("window.history.go(-1)")
                                    time.sleep(1)
                                    continue

                # if algebra go to week section
                if title.find("Algebra") != -1:
                    try:
                        self.driver.find_element_by_xpath(
                            "/html/body/div[4]/div/main/div[2]/div/div[2]/section/div/div/ul/li[3]/div/nav/a[2]").click()
                    except Exception:
                        self.driver.find_element_by_xpath(
                            "/html/body/div[4]/div/main/div[2]/div/div[2]/section/div/div/ul/li[3]/div/nav/a[2]").click()

                # find all assigment cards
                a = self.driver.find_elements_by_css_selector(
                    ".current.state-visible .snap-activity.snap-asset.activity.assign.modtype_assign .asset-wrapper .activityinstance .snap-asset-content .snap-asset-link .mod-link")

                print(a)

                # only do first assigments for enlighs cuz she makes every notes page labeled as assignement...
                # skip for now - she is on google classroom
                if title.find("English") != -1:
                    index += 1
                    found_index += 1
                    if class_ is not None:
                        satisfied = True

                    if found_index == 4:
                        satisfied = True
                    continue

                index = 0
                while index < len(a):
                    if index == 0:
                        a[0].click()
                        try:
                            self.driver.find_element_by_css_selector(".fileuploadsubmission a").click()
                        except Exception:
                            pass
                        self.driver.execute_script("window.history.go(-1)")
                        time.sleep(.5)
                        index += 1
                    else:
                        a = self.driver.find_elements_by_css_selector(
                            ".current.state-visible .snap-activity.snap-asset.activity.assign.modtype_assign .asset-wrapper .activityinstance .snap-asset-content .snap-asset-link .mod-link")

                        a[index].click()
                        try:
                            self.driver.find_element_by_css_selector(".fileuploadsubmission a").click()
                        except Exception:
                            pass
                        self.driver.execute_script("window.history.go(-1)")
                        time.sleep(.5)
                        index += 1

                await self.upload_files(ctx, title + " Work")

                # go back
                if title.find("Algebra") != -1:
                    self.driver.execute_script("window.history.go(-2)")
                else:
                    self.driver.execute_script("window.history.go(-1)")
                time.sleep(1)
                index += 1
                found_index += 1
                if class_ is not None:
                    satisfied = True

                if found_index == 4:
                    satisfied = True

    def check_logged_in(self):
        try:
            self.driver.get("https://neisd.mrooms.net/my/")
            self.driver.find_element_by_id("snap-pm-user-profile")
            return True
        except Exception:
            return False

    def get_account_name(self):
        try:
            self.driver.get("https://neisd.mrooms.net/my/")
            a = self.driver.find_element_by_css_selector("#page-mast h1")
            return a.text
        except Exception:
            return "Error: You may not be logged in! Check with 'status'"

    def logout(self):
        try:
            self.driver.find_element_by_css_selector(".js-snap-pm-trigger").click()
            time.sleep(.5)
            self.driver.find_element_by_id("snap-pm-logout").click()
            return True
        except Exception:
            return False

    def clean_traces(self):
        self.driver.get("https://neisd.mrooms.net/report/usersessions/user.php")
        a = self.driver.find_elements_by_css_selector(".lastcol a")
        index = 0
        while index < len(a):
            if index == 0:
                a[0].click()
                index += 1
            else:
                a = self.driver.find_elements_by_css_selector(".lastcol a")
                a[0].click()
                index += 1
        return index