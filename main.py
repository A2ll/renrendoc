import os
import random
import re
from time import sleep
import requests
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.options import Options as Firefox_Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from lxml import etree
from loguru import logger


def picture_get(html_text):  # 通过网页的html代码获取到图片地址并下载
    ret = re.findall('img src=\"https://.*?\"|data-src=\".*?\"', html_text)
    num = len(ret)
    logger.info('总图片数量：{}张'.format(num))
    try:
        os.mkdir('image')
    except Exception as err:
        logger.warning(err)
    x = 0
    logger.info('开始获取图片')
    for imgurl in ret:
        imgurl = imgurl.rstrip('\"')
        imgurl = imgurl.lstrip('data-src=\"//')
        imgurl = imgurl.lstrip('img src=\"https://')
        try:
            imgres = requests.get('https://' + imgurl)  # 添加'https://'，组成完整网站地址
            with open("image/{}.jpg".format(x), "wb") as f:
                f.write(imgres.content)
                x += 1
        except Exception as err:
            logger.warning('err')
            logger.warning("第", x, "张,下载失败")
        sleep(random.uniform(2, 5))
    logger.info('获取完成！')


def get_html_text(url):  # 获取人人文档网站html页面代码
    # binary = FirefoxBinary('D:\\Program Files\\Mozilla Firefox\\firefox.exe')  # 设置浏览器程序
    # driver = webdriver.Firefox(firefox_binary=binary)  # 设置Firefox浏览器
    # 上述设置方式被弃用，使用会有警告提示
    firefox_options = Firefox_Options()
    firefox_options.binary = r'D:\Program Files\Mozilla Firefox\firefox.exe'
    s = Service(r"driver/geckodriver.exe")
    driver = webdriver.Firefox(service=s, options=firefox_options)  # 指定 geckodirver 的位置
    driver.implicitly_wait(20)  # 隐形等待时间，等待网页加载完成
    driver.get(url)  # 打开url网页
    html = etree.HTML(driver.page_source)  # 用来解析字符串格式的HTML文档对象，将传进去的字符串转变成_Element对象。用于调用xpath()方法
    price = html.xpath('// *[ @ id = "spanpage"]/text()')  # 获取人人文档总页数
    num = int(price[0]) / 5 + 3  # 计算需要加载全部文档的点击次数
    logger.info(num)
    button = driver.find_element(By.XPATH, '//*[@id="ntip2"]')  # 定位元素位置
    view_xpath = driver.find_element(By.XPATH, '//*[@id="outer_page_more"]')
    button.click()
    i = 0
    while i < num:
        driver.execute_script("arguments[0].click();", button)  # 模拟点击按钮
        sleep(1)
        driver.execute_script("arguments[0].scrollIntoView();", view_xpath)  # 滑动至view_xpath中元素位置
        sleep(1)
        driver.execute_script('window.scrollBy(0,-800)')  # 向上滚动浏览器800个像素数。
        i = i + 1
        sleep(random.uniform(5, 9))
        driver.execute_script('window.scrollBy(0,300)')  # 向上滚动浏览器800个像素数。
    logger.info('加载完成，获取页面')
    html_str = driver.page_source
    get_html = "temp.html"
    f = open(get_html, 'wb')
    f.write(driver.page_source.encode("gbk", "ignore"))
    f.close()
    return html_str


if __name__ == '__main__':
    target_url = 'https://www.renrendoc.com/paper/227293095.html?fs=1'
    html_data = get_html_text(target_url)
    picture_get(html_data)
