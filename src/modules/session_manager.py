from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import logging
import os
import time

class SessionManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("初始化 SessionManager")
        self.chrome_options = self._init_chrome_options()
        self.logger.info("Chrome选项初始化成功")
    
    def _init_chrome_options(self):
        """初始化Chrome选项"""
        options = Options()
        
        # 基础设置
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        # 禁用不必要的功能
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-notifications')
        
        # 设置窗��
        options.add_argument('--window-size=1024,768')
        options.add_argument('--start-maximized')
        
        # 设置用户代理
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36')
        
        # 禁用自动化提示
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        
        # 设置性能参数
        prefs = {
            'profile.default_content_setting_values': {
                'notifications': 2,
            },
            'credentials_enable_service': False,
            'profile.password_manager_enabled': False
        }
        options.add_experimental_option('prefs', prefs)
        
        return options
    
    def open_login_window(self):
        """打开登录窗口并获取登录结果"""
        try:
            self.logger.debug("Opening login window...")
            
            driver = None
            try:
                # 更新 Chrome 选项
                options = Options()
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--disable-gpu')
                options.add_argument('--ignore-certificate-errors')  # 忽略证书错误
                options.add_argument('--ignore-ssl-errors')         # 忽略 SSL 错误
                options.add_argument('--disable-web-security')      # 禁用 Web 安全策略
                options.add_argument('--allow-running-insecure-content')  # 允许不安全内容
                options.add_argument('--disable-software-rasterizer')     # 禁用软件光栅化
                
                # 添加实验性选项
                options.add_experimental_option('excludeSwitches', ['enable-logging'])  # 禁用日志
                
                driver = webdriver.Chrome(options=options)
                driver.set_page_load_timeout(30)  # 设置页面加载超时
                
                # 访问登录页面
                self.logger.debug("Navigating to login page...")
                driver.get('https://mp.toutiao.com/auth/page/login')
                
                # 等待登录完成
                self.logger.debug("Waiting for login completion...")
                while True:
                    current_url = driver.current_url
                    if 'login' not in current_url:
                        # 登录成功，等待页面完全加载
                        self.logger.debug("Login successful, waiting for page load...")
                        time.sleep(5)  # 等待页面加载
                        
                        try:
                            # 打印页面源码用于调试
                            self.logger.debug("Current page source:")
                            self.logger.debug(driver.page_source)
                            
                            # 更新用户名选择器
                            selectors = [
                                ".menu-title",  # 菜单标题中的用户名
                                ".auth-avator-name",  # 头像区域的用户名
                                "//div[contains(@class, 'menu-title')]/text()",  # XPath方式
                                "//div[contains(@class, 'auth-avator-name')]/text()"  # XPath方式
                            ]
                            
                            # 修改用户名提取逻辑
                            for selector in selectors:
                                try:
                                    if selector.startswith("//"):
                                        element = WebDriverWait(driver, 5).until(
                                            EC.presence_of_element_located((By.XPATH, selector))
                                        )
                                    else:
                                        element = WebDriverWait(driver, 5).until(
                                            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                                        )
                                    
                                    text = element.text.strip()
                                    self.logger.debug(f"Found element with selector {selector}: {text}")
                                    
                                    if text:
                                        # 处理"晚上好，PenpoAI创意"这样的格式
                                        if "，" in text:
                                            username = text.split("，")[1].strip()
                                        elif "," in text:
                                            username = text.split(",")[1].strip()
                                        else:
                                            username = text
                                        
                                        if username:
                                            self.logger.debug(f"Successfully extracted username: {username}")
                                            break
                                except Exception as e:
                                    self.logger.debug(f"Selector {selector} failed: {str(e)}")
                                    continue
                            
                            if not username:
                                # 如果还是没有找到用户名，尝试查找所有可能的元素
                                self.logger.debug("Trying to find all possible elements...")
                                elements = driver.find_elements(By.CSS_SELECTOR, "*")
                                for elem in elements:
                                    try:
                                        text = elem.text.strip()
                                        if text and ("AI" in text or "创意" in text):
                                            self.logger.debug(f"Found potential username element: {text}")
                                            username = text
                                            break
                                    except:
                                        continue
                            
                            if not username:
                                raise Exception("无法找到用户名元素")
                            
                            # 获取 cookies
                            cookies = driver.get_cookies()
                            
                            return {
                                'success': True,
                                'user_info': {'name': username},
                                'cookies': cookies
                            }
                        except Exception as e:
                            self.logger.error(f"Error getting user info: {str(e)}")
                            return {
                                'success': False,
                                'error': f"获取用户信息失败: {str(e)}"
                            }
                    
                    time.sleep(1)
                    
            finally:
                if driver:
                    try:
                        driver.quit()
                    except:
                        pass
                    
        except Exception as e:
            self.logger.error(f"Error opening login window: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_articles(self, cookies: list) -> dict:
        """获取文章列表"""
        try:
            self.logger.info("开始获取文章列表")
            driver, wait = self.create_session()
            
            try:
                # 访问今日头条主页
                driver.get("https://www.toutiao.com")
                
                # 添加 cookies
                for cookie in cookies:
                    if 'name' in cookie and 'value' in cookie:
                        cookie_dict = {
                            'name': cookie['name'],
                            'value': cookie['value'],
                            'domain': cookie.get('domain', '.toutiao.com'),
                            'path': cookie.get('path', '/'),
                        }
                        driver.add_cookie(cookie_dict)
                
                # 访问创作者中心
                driver.get("https://mp.toutiao.com/profile_v4/graphic/articles")
                
                # 等待文章列表加载
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='article-item']")))
                
                # 获取文章列表
                articles = []
                article_elements = driver.find_elements(By.CSS_SELECTOR, "[class*='article-item']")
                
                for elem in article_elements:
                    try:
                        article = {
                            'title': elem.find_element(By.CSS_SELECTOR, "[class*='title']").text.strip(),
                            'create_time': int(elem.get_attribute('data-create-time') or 0),
                            'digg_count': int(elem.find_element(By.CSS_SELECTOR, "[class*='digg']").text or 0),
                            'comment_count': int(elem.find_element(By.CSS_SELECTOR, "[class*='comment']").text or 0),
                            'read_count': int(elem.find_element(By.CSS_SELECTOR, "[class*='read']").text or 0),
                            'impression_count': int(elem.find_element(By.CSS_SELECTOR, "[class*='impression']").text or 0)
                        }
                        articles.append(article)
                    except Exception as e:
                        self.logger.warning(f"解析文章信息出错: {str(e)}")
                        continue
                
                driver.quit()
                return {
                    'success': True,
                    'articles': articles
                }
                
            except Exception as e:
                self.logger.error(f"获取文章列表失败: {str(e)}")
                driver.quit()
                return {
                    'success': False,
                    'error': str(e)
                }
                
        except Exception as e:
            self.logger.error(f"创建会话失败: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }