from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from zipfile import ZipFile 
import os
import time, shutil, requests

SCROLL_PAUSE_TIME = 2

def downloadVideo(driver,link,fname="default"):
    downloadedVids=[]
    script='window.open("'+link+'");'
    driver.execute_script(script)
    driver.switch_to.window(driver.window_handles[1])
    # driver.get(link)
    videoSource=driver.find_elements_by_xpath("//video[@class='tWeCl']")
    vs=videoSource[0].get_attribute('src')
    fname=vs[vs.rfind('/')+1:vs.find('?')]
    if videoSource not in downloadedVids:
        downloadHelper(fname,vs)
        downloadedVids.append(videoSource)
    driver.close()
    driver.switch_to.window(driver.window_handles[0])

def zip(files):
    with ZipFile('all\\Pics.zip','w') as zip:
        for f in files:
            zip.write(f)
            os.remove(f)        

def downloadPicture(driver,link): 
    # TODO: Handle a video in between a multiple post
    script='window.open("'+link+'");'
    driver.execute_script(script)
    driver.switch_to.window(driver.window_handles[1])
    # driver.get(link)
    downloadedPics=[]
    fNames=[]
    images=driver.find_elements_by_xpath("//div[@class='KL4Bh']")
    multi=driver.find_elements_by_xpath("//button[@class='  _6CZji']")
    if multi:
        while multi:
            for img in images:
                if img not in downloadedPics:
                    src=img.find_element_by_tag_name('img').get_attribute('src')
                    fname=src[src.rfind('/')+1:src.find('?')]
                    downloadHelper(fname,src)
                    fNames.append(fname)
                    downloadedPics.append(img)
            multi[0].click()
            multi=driver.find_elements_by_xpath("//button[@class='  _6CZji']")
            images=driver.find_elements_by_xpath("//div[@class='KL4Bh']")
        # zip(fNames)
    else:
        src=images[0].find_element_by_tag_name('img').get_attribute('src')
        fname=src[src.rfind('/')+1:src.find('?')]
        downloadHelper(fname,src)
    driver.close()
    driver.switch_to.window(driver.window_handles[0])


def addDiv(driver,divs,doneDivs):
    for div in divs:
        if div not in doneDivs:
            posts=div.find_elements_by_xpath("div[@class='v1Nh3 kIKUG  _bz0w']")
            for post in posts:
                a=post.find_element_by_tag_name('a')
                multiple=a.find_elements_by_xpath("div[@class='u7YqG']")
                if not multiple or multiple and multiple[0].find_element_by_css_selector('span').get_attribute("aria-label") =='Carousel':
                    # download photos
                    downloadPicture(driver,a.get_attribute("href"))
                else:
                    # download videos
                    downloadVideo(driver,a.get_attribute("href"))
            doneDivs.append(div)


def login(driver,em="",pas=""):
    email=driver.find_elements_by_xpath("//input[@class='_2hvTZ pexuQ zyHYP']")[0]
    password=driver.find_elements_by_xpath("//input[@class='_2hvTZ pexuQ zyHYP']")[1]    
    email.send_keys(em)
    password.send_keys(pas)
    driver.execute_script('document.getElementsByClassName("_0mzm- sqdOP  L3NKy       ")[0].click()')

def scroll(driver,doneDivs,extract=False):
        # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")
    if extract:
        divs=driver.find_elements_by_xpath("//div[@class='Nnq7C weEfm']")
        addDiv(driver,divs,doneDivs)
    while True:
    # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        if extract:
            divs=driver.find_elements_by_xpath("//div[@class='Nnq7C weEfm']")
            addDiv(driver,divs,doneDivs)
        # Wait to load page
        # time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


def downloadHelper(fileName, url):
    folder="all\\"
    if not os.path.isdir(folder):
        os.mkdir(folder)
    response = requests.get(url, stream=True)
    with open(folder+fileName, 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)


def downloadAll(username,email="",password=""):
    start=time.time()
    doneDivs=[]
    options=webdriver.ChromeOptions()
    # options.add_argument('headless')
    driver=webdriver.Chrome(options=options)
    domain = "https://www.instagram.com"
    user ='/'+username
    driver.get(domain+user)

    res=driver.find_elements_by_xpath("//div[@class='Nd_Rl _2z6nI']")

    if res:
        link=driver.find_elements_by_xpath("//a[@class='hUQXy']")[0].get_attribute('href')
        driver.get(link)
        if email == "" or password == "":
            driver.close()
            raise Exception("User is private, please provide login details!")
        
        print("Logging into the account..")
        login(driver,email,password)
        print("Login Successful!")
        
        time.sleep(2)

        print("Redirecting to target user...",end=" ")
        driver.get(domain+user)
        print("Done!")

    print("Collecting Post Links and Downloading...",end=" ")
    scroll(driver,doneDivs,True)
    print("Done! ",end=" ")
    end=time.time()
    print(str(len(doneDivs)*3)+" Posts Scrapped.")
    print("All Done!")
    seconds = end-start
    minutes = seconds / 60
    seconds = seconds % 60
    t="{:0>2} minutes:{:05.2f} seconds".format(int(minutes),seconds)
    print("Time Taken: "+t)
    driver.close()

def downloadWithLink(link):
    start=time.time()    
    driver=webdriver.Chrome()
    if driver.find_elements_by_xpath("//video[@class='tWeCl']"):
        downloadVideo(driver,link)
    else:
        downloadPicture(driver,link)
    end=time.time()
    seconds = end-start
    minutes = seconds // 60
    seconds = seconds % 60
    t="{:0>2} minutes:{:05.2f} seconds".format(int(minutes),seconds)
    print("Time Taken: "+t)

# * Example Usage

name="USERNAME OF THE ACCOUNT TO SCRAP" 
# ! If target account is private, enter the details of the account which is following it.
AUTH_EMAIL="USERNAME OR EMAIL"
AUTH_PASS="PASSWORD"

downloadWithLink("https://www.instagram.com/p/BumEu9dlXn5/") # * Downloads the pciture(s) or video(s) in the specified link of the post
downloadAll(name,AUTH_EMAIL,AUTH_PASS) # * Downloads all the pictures and video uploaded by the given user (name)

