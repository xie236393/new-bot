from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import logging
import os
import time

logger = logging.getLogger(__name__)

def fetch_articles(cookies=None):
    """获取头条文章列表及统计数据"""
    driver = None
    try:
        # 设置Chrome选项
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--ignore-certificate-errors')
        # options.add_argument('--headless')  # 暂时注释掉无头模式便于调试
        
        # 增加页面加载策略
        options.page_load_strategy = 'eager'  # 使用eager策略加快加载
        
        # 创建Chrome实例
        driver = webdriver.Chrome(options=options)
        
        # 设置更合理的超时时间
        driver.set_page_load_timeout(60)  # 增加到60秒
        driver.set_script_timeout(60)
        driver.implicitly_wait(20)  # 增加隐式等待时间
        
        # 先访问头条域名
        logger.info("访问头条域名...")
        driver.get('https://mp.toutiao.com')
        
        # 增加显式等待
        wait = WebDriverWait(driver, 20)
        
        # 添加cookies
        logger.info("添加cookies...")
        if isinstance(cookies, str):
            cookies = json.loads(cookies)
            
        for cookie in cookies:
            try:
                if isinstance(cookie, str):
                    cookie = json.loads(cookie)
                    
                if 'name' in cookie and 'value' in cookie:
                    cookie_dict = {
                        'name': cookie['name'],
                        'value': cookie['value'],
                        'domain': cookie.get('domain', '.toutiao.com'),
                        'path': cookie.get('path', '/')
                    }
                    driver.add_cookie(cookie_dict)
            except Exception as e:
                logger.warning(f"添加cookie失败: {e}")
                continue
        
        # 访问文章列表页面
        logger.info("访问文章列表页面...")
        driver.get('https://mp.toutiao.com/profile_v4/graphic/articles')
        
        # 使用显式等待检查页面加载
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".article-card")))
        except Exception as e:
            logger.warning("等待文章列表超时，尝试其他选择器...")
            # 保存页面源码以供分析
            with open('error_page.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            
            # 尝试其他可能的选择器
            selectors = [
                ".byte-table-tbody tr",
                ".article-list-item",
                "[data-log-click='article_title']"
            ]
            
            for selector in selectors:
                try:
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    logger.info(f"找到替代选择器: {selector}")
                    break
                except:
                    continue
        
        # 获取文章列表
        articles = []
        article_elements = driver.find_elements(By.CSS_SELECTOR, ".article-card")
        
        if not article_elements:
            logger.warning("使用主选择器未找到文章，尝试备用选择器...")
            # 尝试其他选择器
            for selector in [".byte-table-tbody tr", ".article-list-item"]:
                article_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if article_elements:
                    logger.info(f"使用备用选择器成功: {selector}")
                    break
        
        logger.info(f"找到 {len(article_elements)} 个文章元素")
        
        if not article_elements:
            logger.error("未找到任何文章元素")
            return []
            
        for elem in article_elements:
            try:
                article = {}
                
                # 获取标题
                title = elem.find_element(By.CSS_SELECTOR, ".title").text.strip()
                article['title'] = title
                
                # 获取发布时间
                try:
                    time_element = elem.find_element(By.CSS_SELECTOR, ".create-time")
                    article['publish_time'] = time_element.text.strip()
                except Exception as e:
                    logger.warning(f"获取发布时间失败: {e}")
                    article['publish_time'] = "-"
                
                # 获取统计数据列表
                stat_elements = elem.find_elements(By.CSS_SELECTOR, "ul.count li")
                
                # 处理每个统计数据
                for stat in stat_elements:
                    text = stat.text.strip()
                    if '展现' in text:
                        article['show_count'] = text.replace('展现', '').strip()
                    elif '阅读' in text:
                        article['read_count'] = text.replace('阅读', '').strip()
                    elif '点赞' in text:
                        article['digg_count'] = text.replace('点赞', '').strip()
                    elif '评论' in text:
                        article['comment_count'] = text.replace('评论', '').strip()
                
                # 确保所有字段都存在
                for field in ['digg_count', 'show_count', 'read_count', 'comment_count']:
                    if field not in article:
                        article[field] = '0'
                
                articles.append(article)
                logger.info(f"解析文章: {article}")
                
            except Exception as e:
                logger.warning(f"解析文章元素失败: {e}")
                continue
        
        return articles
        
    except Exception as e:
        logger.error(f"获取文章列表失败: {e}")
        return []
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass