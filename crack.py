import os
import time
from io import BytesIO
from PIL import Image
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from os import listdir

# USERNAME = '15874295385'
# PASSWORD = 'fpdpvx119'

TEMPLATES_FOLDER = 'templates/'


class CrackWeiboSlide():
    def __init__(self,USERNAME,PASSWORD):
        self.url = 'https://passport.weibo.cn/signin/login?entry=mweibo&r=https://weibo.cn/'
        #self.url = 'https://weibo.cn'
        self.browser = webdriver.Chrome()
        self.wait = WebDriverWait(self.browser, 20)
        self.username = USERNAME
        self.password = PASSWORD
    
    def __del__(self):
        self.browser.close()
    
    def open(self):
        """
        打开网页输入用户名密码并点击
        :return: None
        """
        self.browser.get(self.url)
        # login_name = WebDriverWait(self.browser, 10).until(
        #     EC.visibility_of_element_located((By.ID, "loginName"))
        # )
        #username = self.wait.until(EC.visibility_of_element_located((By.ID, "loginName")))
        username = WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.ID, "loginName"))
        )
        password = self.browser.find_element_by_id("loginPassword")
        submit = self.wait.until(EC.element_to_be_clickable((By.ID, 'loginAction')))
        username.send_keys(self.username)
        password.send_keys(self.password)
        submit.click()
    
    def get_position(self):
        """
        获取验证码位置
        :return: 验证码位置元组
        """
        try:
            img = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'patt-shadow')))
        except TimeoutException:
            print('未出现验证码')
            self.open()
        time.sleep(2)
        location = img.location
        size = img.size
        top, bottom, left, right = location['y'], location['y'] + size['height'], location['x'], location['x'] + size[
            'width']
        return (top, bottom, left, right)
    
    def get_screenshot(self):
        """
        获取网页截图
        :return: 截图对象
        """
        screenshot = self.browser.get_screenshot_as_png()
        screenshot = Image.open(BytesIO(screenshot))
        return screenshot
    
    def get_image(self, name='captcha.png'):
        """
        获取验证码图片
        :return: 图片对象
        """
        top, bottom, left, right = self.get_position()
        print('验证码位置', top, bottom, left, right)
        screenshot = self.get_screenshot()
        captcha = screenshot.crop((left, top, right, bottom))
        captcha.save(name)
        return captcha
    def get_image_advanced(self,name='captcha.png'):
        """
        获取验证码图片
        :return: 图片对象
        """
        top, bottom, left, right = self.get_position()
        print('验证码位置', top, bottom, left, right)
        screenshot = self.get_screenshot()
        captcha = screenshot.crop((left, top, right, bottom))
        captcha.save('captcha.png')
        """
        匹配图片
        :param image: 图片
        :return: 拖动顺序
        """
        flag = False
        current_fag = Image.open('captcha.png')
        count = 0
        for template_name in listdir(TEMPLATES_FOLDER):
            flag = False
            print('正在匹配第' + str(count) + '张图片' + '-' * 40)
            count += 1
            template = Image.open(TEMPLATES_FOLDER + template_name)
            if self.same_image(current_fag, template):
                flag = True
                break
            else:
                print('第' + str(count - 1) + '张图片匹配失败' + '-' * 40)
                continue
        if flag == False:
            captcha.save(TEMPLATES_FOLDER + name)
            return captcha
    def is_pixel_equal(self, image1, image2, x, y):
        """
        判断两个像素是否相同
        :param image1: 图片1
        :param image2: 图片2
        :param x: 位置x
        :param y: 位置y
        :return: 像素是否相同
        """
        # 取两个图片的像素点
        pixel1 = image1.load()[x, y]
        pixel2 = image2.load()[x, y]
        threshold = 20
        if abs(pixel1[0] - pixel2[0]) < threshold and abs(pixel1[1] - pixel2[1]) < threshold and abs(
                pixel1[2] - pixel2[2]) < threshold:
            return True
        else:
            return False
    
    def same_image(self, image, template):
        """
        识别相似验证码
        :param image: 待识别验证码
        :param template: 模板
        :return:
        """
        # 相似度阈值
        threshold = 0.99
        count = 0
        for x in range(image.width):
            for y in range(image.height):
                # 判断像素是否相同
                if self.is_pixel_equal(image, template, x, y):
                    count += 1
        result = float(count) / (image.width * image.height)
        if result > threshold:
            print('成功匹配')
            return True
        return False
    
    def detect_image(self, image):
        """
        匹配图片
        :param image: 图片
        :return: 拖动顺序
        """
        for template_name in listdir(TEMPLATES_FOLDER):
            print('正在匹配', template_name)
            template = Image.open(TEMPLATES_FOLDER + template_name)
            if self.same_image(image, template):
                # 返回顺序
                numbers = [int(number) for number in list(template_name.split('.')[0])]
                print('拖动顺序', numbers)
                return numbers
    
    def move(self, numbers):
        """
        根据顺序拖动
        :param numbers:
        :return:
        """
        # 获得四个按点
        try:
            circles = self.browser.find_elements_by_css_selector('.patt-wrap .patt-circ')
            dx = dy = 0
            for index in range(4):
                circle = circles[numbers[index] - 1]
                # 如果是第一次循环
                if index == 0:
                    # 点击第一个按点
                    ActionChains(self.browser) \
                        .move_to_element_with_offset(circle, circle.size['width'] / 2, circle.size['height'] / 2) \
                        .click_and_hold().perform()
                else:
                    # 小幅移动次数
                    times = 30
                    # 拖动
                    for i in range(times):
                        ActionChains(self.browser).move_by_offset(dx / times, dy / times).perform()
                        time.sleep(1 / times)
                # 如果是最后一次循环
                if index == 3:
                    # 松开鼠标
                    ActionChains(self.browser).release().perform()
                else:
                    # 计算下一次偏移
                    dx = circles[numbers[index + 1] - 1].location['x'] - circle.location['x']
                    dy = circles[numbers[index + 1] - 1].location['y'] - circle.location['y']
            return True
        except Exception as identifier:
            return False

    def crack(self):
        """
        破解入口
        :return:
        """
        self.open()
        # 获取验证码图片
        image = self.get_image('captcha.png')
        numbers = self.detect_image(image)
        flag = self.move(numbers)
        time.sleep(10)
        if flag == False:
            print('识别失败,正在重试')
            return False
        else:
            print('识别结束')
            return True

    def main(self):
        """
        批量获取验证码
        :return: 图片对象
        """
        count = 0
        count_0 = 0
        while True:
            self.open()
            self.get_image_advanced(str(count) + '.png')
            count += 1
            count_0 = 0
            for template_name in listdir(TEMPLATES_FOLDER):
                count_0 += 1
            print('图片数量为：  ' + str(count_0))
            if count_0 == 24:
                break
                

if __name__ == '__main__':
    crack = CrackWeiboSlide('17751790203','a597911628')
    crack.main()
    #crack.crack()
