import time
import uuid
from array import array
from io import BytesIO
from pylab import *

from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BaseGeetestCrack(object):

    "验证码破解基础类"

    def __init__(self, driver):
        self.driver = driver
        self.driver.maximize_window()

    def input_by_id(self, text=u"恒大", css_selector='input.f14'):
        '''
        :param text:输入框内文字
        :param element_id:定位输入框的id
        :return:
        '''

        input_el = self.driver.find_element_by_css_selector(css_selector)
        input_el.clear()
        input_el.send_keys(text)
        time.sleep(3.5)

    def click_by_id(self, element_id='btn_query'):
        '''
        :param element_id:查询按钮的位置
        :return:
        '''

        search_el = self.driver.find_element_by_id(element_id)
        search_el.click()
        time.sleep(3.5)

    def calculate_slider_offset(self):
        '''
        计算滑块滑动位置，必须在click事件之后触发
        :return:Number
        '''
        img1 = self.crop_captcha_image()
        self.drag_and_drop(x_offset=5)
        img2 = self.crop_captcha_image()
        w1, h1 = img1.size
        w2, h2 = img2.size
        if w1 != w2 or h1 != h2:
            return False
        left = 0
        flag = False
        for i in range(100, w1):
            for j in range(h1):
                if not self.is_pixel_equal(img1, img2, i, j):
                    left = i
                    flag = True
                    break
            if flag:
                break
        if left == 100:
            left -= 4
        return left
        print(w1, h1)

    def is_pixel_equal(self, img1, img2, x, y):
        pix1 = array(img1.convert('L'))
        pix2 = array(img2.convert('L'))
        '''
        伽马变换公式:s=cr^gamma r∈[0,1]
        r为原图的灰度化图片
        '''
        C = 1
        gamma = 20
        pix1_after = C * (pix1 / 255) ** gamma
        pix2_after = C * (pix2 / 255) ** gamma
        result = pix1_after[y, x] - pix2_after[y, x]
        if result < 2:
            return True
        else:
            return False

    def crop_captcha_image(self, element_class='gt_box'):
        '''
        截取验证码图片
        :param element_id:验证码图片容器
        :return: StringIO,图片内容
        '''
        '''
        下面的是通过获取location来截图，但是图方便直接用坐标了
        '''
        captcha_el = self.driver.find_element_by_class_name(element_class)
        # location= captcha_el.location
        # size = captcha_el.size
        # left = int(location['x'])
        # top = int(location['y'])
        left = 1152
        top = 550
        # right = left + int(size['width'])
        # bottom = top + int(size['height'])
        right = left+520
        bottom = top+232
        print(left, top, right, bottom)

        screenshot = self.driver.get_screenshot_as_png()

        screenshot = Image.open(BytesIO(screenshot))
        captcha = screenshot.crop((left, top, right, bottom))
        captcha.save('%s.png' % uuid.uuid1())
        return captcha

    def get_browser_name(self):
        '''
        获取当前浏览器名称
        :return: TODO
        '''

        return str(self.driver).split('.')[2]

    def drag_and_drop(self, x_offset=0, y_offset=0, element_class='gt_slider_knob'):
        '''
        拖拽滑块
        :param x_offset:滑块x轴移动的位置
        :param y_offset:滑块y轴移动的位置
        :param element_class:滑块的元素
        :return:
        '''

        dragger = self.driver.find_element_by_class_name(element_class)
        action = ActionChains(self.driver)
        action.drag_and_drop_by_offset(dragger, x_offset, y_offset).perform()
        time.sleep(8)

    def move_to_element(self, element_class='gt_slider_knob'):
        '''
        鼠标移到目标元素上
        :param element_class:目标网页元素
        :return:
        '''
        time.sleep(3)
        element = self.driver.find_element_by_class_name(element_class)
        action = ActionChains(self.driver)
        action.move_to_element(element).perform()
        time.sleep(4.5)

    def crack(self):
        '''
        执行破解程序
        :return:
        '''
        return NotImplementedError



class GeetestCrack(BaseGeetestCrack):

    '''工商滑动验证码破解类'''

    def __init__(self, driver):
        super(GeetestCrack, self).__init__(driver)

    def crack(self):
        '''执行破解程序'''
        self.input_by_id()
        self.click_by_id()
        time.sleep(2)
        x_offset = self.calculate_slider_offset()
        self.drag_and_drop(x_offset=x_offset)


driver = webdriver.Chrome('D:\chromedriver\chromedriver.exe')
driver.get('http://www.gsxt.gov.cn/index.html')
wait = WebDriverWait(driver, 10)
wait.until(EC.presence_of_element_located((By.ID, 'btn_query')))
cracker = GeetestCrack(driver)
cracker.crack()
print(driver.get_window_size())
time.sleep(3)
driver.save_screenshot('screen.png')
driver.quit()