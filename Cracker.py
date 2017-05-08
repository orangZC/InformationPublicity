import time
import uuid
import re
import random
import requests

from io import BytesIO
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from PIL import Image

class GeetestCrack(object):
    def __init__(self, driver):
        self.driver = driver
        driver.maximize_window()

    def input_by_id(self, text = '恒大', element_id = 'keyword'):
        input_elem = self.driver.find_element_by_id(element_id)
        input_elem.clear()
        input_elem.send_keys(text)
        time.sleep(2)

    def click_by_id(self, element_id = 'btn_query'):
        click_elem = self.driver.find_element_by_id(element_id)
        click_elem.click()
        time.sleep(2)

    def get_merge(self, filename, location_list):

        '''
        :param filename:传入的被打乱的图片 
        :param location_list: 图片各部分的位置
        :return: 
        '''

        im = filename

        '''im_list_up即图片上半部分的组成部分，
        由于图片在变换时是上下进行颠倒，因此我们可以判断，
        若一个图片的css中显示它的location为-58，
        那么即可判断它原来的位置在58到116，
        同时也位于图片的上半部分
        im_list_down同理
        '''

        im_list_up = []
        im_list_down = []

        for location in location_list:
            if location['y'] == -58:
                im_list_up.append(im.crop((abs(location['x']), 58, abs(location['x']) + 10, 166)))
            if location['y'] == 0:
                im_list_down.append(im.crop((abs(location['x']), 0, abs(location['x'])+10, 58)))

        new_im = Image.new('RGB', (260, 116))

        '''
        这里的两个for循环的意思是，把按顺序截取的图片部分（按照排序好的图片截取）
        进行拼合，从左上角开始
        先拼合上面的部分，再拼合下面的部分
        '''

        x_offset = 0
        for image in im_list_up:
            new_im.paste(image, (x_offset, 0))
            x_offset += image.size[0]

        x_offset = 0
        for image in im_list_down:
            new_im.paste(image, (x_offset, 58))
            x_offset += image.size[0]

        return new_im

    def get_image(self, element_class):

        '''
        :param element_class:图片所在的元素 
        :return: 
        '''

        background_images = self.driver.find_elements_by_class_name(element_class)
        location_list = []

        for background_image in background_images:
            location = {}
            location['x'] = int(re.findall("background-image: url\(\"(.*)\"\); background-position: (.*)px (.*)px;",
                                           background_image.get_attribute('style'))[0][1])
            location['y'] = int(re.findall("background-image: url\(\"(.*)\"\); background-position: (.*)px (.*)px;",
                                           background_image.get_attribute('style'))[0][2])
            image_url = re.findall("background-image: url\(\"(.*)\"\); background-position: (.*)px (.*)px;",
                                  background_image.get_attribute('style'))[0][0]
            location_list.append(location)

        imageurl = image_url.replace('webp', 'jpg')
        r = BytesIO(requests.get(imageurl).content)
        jpgfile = Image.open(r)

        new_im = self.get_merge(jpgfile, location_list)
        new_im.save("%s.png" % uuid.uuid4())

        return new_im

    def is_similiar(self, image1, image2, x, y):

        '''
        :param image1:通过getimage方法获取的图片1
        :param image2: 通过getimage方法获取的图片2
        :param x: 图片的x轴
        :param y: 图片的y轴
        :return: 
        '''

        pixel1 = image1.getpixel((x, y))
        pixel2 = image2.getpixel((x, y))


        for i in range(0, 3):
            if abs(pixel1[i]) - abs(pixel2[i]) > 50:
                return False
            else:
                return True

    def get_diff(self, image1, image2):

        '''
        :param image1:进行比对的图片1 
        :param image2: 即逆行比对的图片2
        :return: 
        '''

        for i in range(0, 260):
            for j in range(0, 116):
                if self.is_similiar(image1, image2, i, j) is False:
                    print(i)
                    return i

    def get_track(self, length):

        '''
        :param length:length为需要移动的长度 
        :return: 
        '''

        list = []

        for j in range(3):
            list.append(1)

        length -= 3
        x = random.randint(1, 3)
        while length - x > 5:
            list.append(x)
            length -= x
            x = random.randint(1, 3)

        for i in range(x):
            list.append(1)

        print(list)
        return list

    def drag_and_drop(self, track_list):

        '''
        :param track_list:track_list为需要拖动轨迹的集合，即get_track方法中返回的list 
        :return: 
        '''

        drag_elem = self.driver.find_element_by_class_name('gt_slider_knob')
        location = drag_elem.location
        y = location['y']
        print('this is the height of the element:', y)
        ActionChains(self.driver).move_to_element(to_element = drag_elem).perform()

        #点击元素
        print('click the element')
        ActionChains(self.driver).click_and_hold(on_element = drag_elem).perform()
        time.sleep(0.15)


        #拖拽元素
        print('drag the element')
        track_string = ''
        for track in track_list:
            random_y = random.randint(0, 1)
            track_string = track_string + "{%d, %d}," % (track, y - 472 + random_y)
            ActionChains(self.driver).move_to_element_with_offset(to_element = drag_elem, xoffset = track + 22, yoffset = y + random_y- 472).perform()
            time.sleep(random.randint(1, 20)/400)
        print(track_string)
        ActionChains(self.driver).move_to_element_with_offset(to_element = drag_elem, xoffset = 21, yoffset = y - 472).perform()
        time.sleep(0.1)
        ActionChains(self.driver).move_to_element_with_offset(to_element = drag_elem, xoffset = 21, yoffset = y - 472).perform()
        ActionChains(self.driver).move_to_element_with_offset(to_element = drag_elem, xoffset = 21, yoffset = y - 472).perform()
        time.sleep(0.01)
        ActionChains(self.driver).move_to_element_with_offset(to_element = drag_elem, xoffset = 21, yoffset = y - 472).perform()
        time.sleep(0.02)
        ActionChains(self.driver).move_to_element_with_offset(to_element = drag_elem, xoffset = 21, yoffset = y - 472).perform()
        time.sleep(0.07)
        #松开元素
        print('drop the element')
        ActionChains(self.driver).release(on_element = drag_elem).perform()

    def crack(self):

        raise NotImplementedError

class Cracker(GeetestCrack):
    def __init__(self, driver):
        super(Cracker, self).__init__(driver)

    def crack(self):
        self.input_by_id()
        self.click_by_id()
        time.sleep(3.5)
        WebDriverWait(self.driver, 30).until(lambda the_driver: the_driver.find_element_by_class_name('gt_cut_bg_slice')).is_displayed()
        image1 = self.get_image('gt_cut_bg_slice')
        image2 = self.get_image('gt_cut_fullbg_slice')
        loc = self.get_diff(image1, image2)
        list = self.get_track(loc)
        self.drag_and_drop(list)
        time.sleep(10)

def main():
    driver = webdriver.Chrome('/Users/orange/Downloads/chromedriver')
    driver.get('http://www.gsxt.gov.cn/index.html')
    cracker = Cracker(driver)
    cracker.crack()
    print(driver.get_window_size())
    time.sleep(3)
if __name__ == "__main__":
    main()