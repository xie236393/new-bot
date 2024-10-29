from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class ToutiaoCrawler:
    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait
    
    def get_user_info(self):
        """获取用户信息"""
        user_info = {}
        selectors = {
            'username': ['.user-name', '.username', '.name', '[data-log="username"]', '//span[contains(@class, "name")]'],
            'stats': ['.user-data', '.data-overview', '.count-wrapper', '//div[contains(@class, "data")]']
        }
        
        for selector in selectors['username']:
            try:
                if selector.startswith('//'):
                    username = self.driver.find_element(By.XPATH, selector)
                else:
                    username = self.driver.find_element(By.CSS_SELECTOR, selector)
                user_info['username'] = username.text
                break
            except:
                continue
                
        for selector in selectors['stats']:
            try:
                if selector.startswith('//'):
                    stats = self.driver.find_elements(By.XPATH, selector)
                else:
                    stats = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for stat in stats:
                    text = stat.text
                    if '粉丝' in text:
                        user_info['fans'] = text
                    elif '关注' in text:
                        user_info['following'] = text
                    elif '获赞' in text:
                        user_info['likes'] = text
                break
            except:
                continue
        return user_info
    
    def get_article_list(self):
        """获取文章列表"""
        articles = []
        selectors = ['.article-card', '.content-item', '.article-item', '//div[contains(@class, "article")]', '//div[contains(@class, "content-item")]']