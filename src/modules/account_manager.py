import sqlite3
import json
import logging
import os
from datetime import datetime
from .session_manager import SessionManager

class Account:
    def __init__(self, username, cookies, status=True, last_check_time=None, user_info=None):
        self.username = username
        self.cookies = cookies
        self.status = status
        self.last_check_time = last_check_time or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.user_info = user_info or {}

class AccountManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("初始化 AccountManager")
        
        # 初始化 SessionManager
        self.session_manager = SessionManager()  # 改为 session_manager
        
        # 初始化数据库
        self.db_path = os.path.join('data', 'accounts.db')
        os.makedirs('data', exist_ok=True)
        
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        
        # 修改账号表结构，添加 cookies 字段
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                cookies TEXT,
                last_login TIMESTAMP,
                status TEXT
            )
        ''')
        self.conn.commit()
        self.logger.info(f"数据库初始化成功: {os.path.abspath(self.db_path)}")

    def add_account(self, username, cookies):
        """添加新账号"""
        try:
            # 检查账号是否已存在
            self.cursor.execute('SELECT * FROM accounts WHERE username = ?', (username,))
            if self.cursor.fetchone():
                return {
                    'success': False,
                    'error': '账号已存在'
                }

            # 确保 cookies 是正确的 JSON 格式
            if isinstance(cookies, (list, dict)):
                cookies_str = json.dumps(cookies)
            elif isinstance(cookies, str):
                # 验证是否为有效的 JSON 字符串
                try:
                    json.loads(cookies)
                    cookies_str = cookies
                except json.JSONDecodeError:
                    return {
                        'success': False,
                        'error': 'Invalid cookies format'
                    }
            else:
                return {
                    'success': False,
                    'error': 'Invalid cookies type'
                }

            # 保存账号信息
            self.cursor.execute('''
                INSERT INTO accounts (username, cookies, last_login, status)
                VALUES (?, ?, CURRENT_TIMESTAMP, 'active')
            ''', (username, cookies_str))
            self.conn.commit()

            return {
                'success': True,
                'message': '账号添加成功'
            }

        except Exception as e:
            self.logger.error(f"Error adding account: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_account(self, username):
        """获取账号信息"""
        try:
            self.cursor.execute('SELECT username, cookies, last_login, status FROM accounts WHERE username = ?', (username,))
            row = self.cursor.fetchone()
            
            if row:
                username, cookies_str, last_login, status = row
                try:
                    cookies = json.loads(cookies_str) if cookies_str else None
                except json.JSONDecodeError:
                    self.logger.error(f"解析 cookies 失败，账号: {username}")
                    cookies = None
                    
                return {
                    'username': username,
                    'cookies': cookies,
                    'last_login': last_login,
                    'status': status
                }
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting account: {str(e)}")
            return None

    def get_all_accounts(self):
        """获取所有账号列表"""
        try:
            self.logger.info("获取所有账号列表")
            accounts = []
            
            self.cursor.execute('SELECT username, cookies, last_login, status FROM accounts')
            rows = self.cursor.fetchall()
            
            for row in rows:
                try:
                    username, cookies_str, last_login, status = row
                    
                    # 尝试解析 cookies
                    try:
                        if cookies_str and isinstance(cookies_str, str):
                            cookies = json.loads(cookies_str)
                        else:
                            cookies = None
                    except json.JSONDecodeError as e:
                        self.logger.error(f"解析 cookies 失败: {str(e)}, 数据: {cookies_str}")
                        cookies = None
                    
                    account = {
                        'username': username,
                        'cookies': cookies,
                        'last_login': last_login,
                        'status': status
                    }
                    accounts.append(account)
                    
                except Exception as e:
                    self.logger.error(f"处理账号数据时出错: {str(e)}")
                    continue
            
            self.logger.info(f"成功获取所有账号，共 {len(accounts)} 个")
            return accounts
            
        except Exception as e:
            self.logger.error(f"获取账号列表失败: {str(e)}")
            return []

    def remove_account(self, username: str) -> bool:
        """删除账号"""
        try:
            self.logger.info(f"删除账号: {username}")
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM accounts WHERE username = ?', (username,))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"账号删除成功: {username}")
            return True
            
        except Exception as e:
            self.logger.error(f"删除账号失败: {str(e)}")
            return False

    def _repair_database(self):
        """修复数据库中的错误数据"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 获取所有账号
            cursor.execute('SELECT username, cookies FROM accounts')
            rows = cursor.fetchall()
            
            for username, cookies_str in rows:
                try:
                    # 尝试解析数据
                    json.loads(cookies_str)
                except json.JSONDecodeError:
                    self.logger.warning(f"发现错误的 cookies 数据，正在修复账号: {username}")
                    # 删除错误数据
                    cursor.execute('DELETE FROM accounts WHERE username = ?', (username,))
                    
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"修复数据库失败: {str(e)}")

    def get_articles(self, username: str) -> list:
        """获取指定账号的文章列表"""
        try:
            self.logger.info(f"获取账号 {username} 的文章列表")
            
            # 获取账号信息
            account = self.get_account(username)
            if not account:
                self.logger.error(f"账号 {username} 不存在")
                return []
                
            if not account.cookies:
                self.logger.error(f"账号 {username} 的 cookies 数据无效")
                return []
                
            # 使用 session_manager 获取文章列表
            result = self.session_manager.get_articles(account.cookies)
            
            if result['success']:
                return result['articles']
            else:
                self.logger.error(f"获取文章列表失败: {result.get('error', '未知错误')}")
                return []
                
        except Exception as e:
            self.logger.error(f"获取文章列表失败: {str(e)}")
            return []