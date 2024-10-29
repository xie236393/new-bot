from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QTableWidget, QTableWidgetItem, 
    QMessageBox, QLabel, QHeaderView, QSplitter,
    QTabWidget
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import logging
from datetime import datetime
from modules.account_manager import AccountManager
from services.article_service import fetch_articles

class ArticleFetchThread(QThread):
    finished = pyqtSignal(list)  # 成功信号
    error = pyqtSignal(str)      # 错误信号
    
    def __init__(self, cookies):
        super().__init__()
        self.cookies = cookies
        self.timeout = 120  # 设置2分钟超时
    
    def run(self):
        try:
            articles = fetch_articles(self.cookies)  # 传入特定账号的 cookies
            if articles is not None:
                self.finished.emit(articles)
            else:
                self.error.emit("获取文章失败")
        except Exception as e:
            self.error.emit(str(e))

class AccountManagerUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.account_manager = AccountManager()
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle('头条账号管理器')
        self.setGeometry(100, 100, 1200, 800)
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)  # 设置边距
        layout.setSpacing(5)  # 设置组件间距
        
        # 创建工具栏容器
        toolbar_widget = QWidget()
        toolbar_widget.setFixedHeight(50)  # 固定工具栏高度
        toolbar_layout = QHBoxLayout(toolbar_widget)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        
        # 添加账号按钮
        add_btn = QPushButton('添加账号')
        add_btn.setFixedWidth(100)
        add_btn.clicked.connect(self.add_account)
        toolbar_layout.addWidget(add_btn)
        
        # 刷新按钮
        refresh_btn = QPushButton('刷新')
        refresh_btn.setFixedWidth(100)
        refresh_btn.clicked.connect(self.refresh_all)
        toolbar_layout.addWidget(refresh_btn)
        
        # 添加状态标签
        self.status_label = QLabel('就绪')
        toolbar_layout.addWidget(self.status_label)
        
        # 添加弹性空间
        toolbar_layout.addStretch()
        
        # 将工具栏添加到主布局
        layout.addWidget(toolbar_widget)
        
        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(True)  # 允许子部件折叠
        
        # 左侧账号列表
        account_widget = self._create_account_widget()
        splitter.addWidget(account_widget)
        
        # 右侧文章信息
        article_widget = self._create_article_widget()
        splitter.addWidget(article_widget)
        
        # 设置分割器比例
        splitter.setSizes([400, 800])
        splitter.setStretchFactor(0, 1)  # 账号列表可伸缩
        splitter.setStretchFactor(1, 2)  # 文章列表可伸缩
        
        # 将分割器添加到主布局
        layout.addWidget(splitter)
        
    def _create_account_widget(self):
        """创建账号列表部件"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)  # 移除边距
        
        # 创建标题容器
        title_widget = QWidget()
        title_widget.setFixedHeight(30)  # 固定标题高度
        title_layout = QHBoxLayout(title_widget)
        title_layout.setContentsMargins(5, 0, 5, 0)
        
        # 添加标题
        title = QLabel('账号列表')
        title.setStyleSheet('font-size: 14px; font-weight: bold;')
        title_layout.addWidget(title)
        
        layout.addWidget(title_widget)
        
        # 创建账号表格
        self.account_table = QTableWidget()
        self.account_table.setColumnCount(4)
        self.account_table.setHorizontalHeaderLabels(['用户名', '状态', '登录时间', '操作'])
        
        # 设置表格样式
        self.account_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                gridline-color: #f5f5f5;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                padding: 4px;
                border: 1px solid #ddd;
                font-weight: bold;
            }
        """)
        
        # 设置表格列宽和调整模式
        header = self.account_table.horizontalHeader()
        # 允许用户调整所有列的宽度
        header.setSectionResizeMode(QHeaderView.Interactive)
        
        # 设置默认列宽
        self.account_table.setColumnWidth(0, 200)  # 用户名列
        self.account_table.setColumnWidth(1, 80)   # 状态列
        self.account_table.setColumnWidth(2, 150)  # 登录时间列
        self.account_table.setColumnWidth(3, 100)  # 操作列
        
        # 设置最小列宽，防止过度缩小
        header.setMinimumSectionSize(60)
        
        # 允许最后一列自动填充剩余空间
        header.setStretchLastSection(True)
        
        # 选择行为
        self.account_table.clicked.connect(self.on_account_selected)
        
        layout.addWidget(self.account_table)
        return widget
        
    def _create_article_widget(self):
        """创建文章信息部件"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)  # 移除边距
        
        # 创建标题容器
        title_widget = QWidget()
        title_widget.setFixedHeight(30)  # 固定标题高度
        title_layout = QHBoxLayout(title_widget)
        title_layout.setContentsMargins(5, 0, 5, 0)
        
        # 添加标题
        title = QLabel('文章信息')
        title.setStyleSheet('font-size: 14px; font-weight: bold;')
        title_layout.addWidget(title)
        
        layout.addWidget(title_widget)
        
        # 创建文章表格
        self.article_table = QTableWidget()
        self.article_table.setColumnCount(6)
        self.article_table.setHorizontalHeaderLabels(['标题', '发布时间', '点赞', '展现', '阅读', '评论'])
        
        # 设置表格样式
        self.article_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                gridline-color: #f5f5f5;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                padding: 4px;
                border: 1px solid #ddd;
                font-weight: bold;
            }
            QHeaderView::section:hover {
                background-color: #e5e5e5;
            }
        """)
        
        # 设置表格列宽和调整模式
        header = self.article_table.horizontalHeader()
        # 允许用户调整所有列的宽度
        header.setSectionResizeMode(QHeaderView.Interactive)
        
        # 设置默认列宽
        self.article_table.setColumnWidth(0, 300)  # 标题列
        self.article_table.setColumnWidth(1, 150)  # 发布时间列
        self.article_table.setColumnWidth(2, 80)   # 点赞列
        self.article_table.setColumnWidth(3, 80)   # 展现列
        self.article_table.setColumnWidth(4, 80)   # 阅读列
        self.article_table.setColumnWidth(5, 80)   # 评论列
        
        # 设置最小列宽，防止过度缩小
        header.setMinimumSectionSize(60)
        
        # 允许标题列自动充剩余空间
        header.setStretchLastSection(True)
        
        layout.addWidget(self.article_table)
        return widget
        
    def refresh_account_table(self):
        """刷新账号列表"""
        try:
            self.status_label.setText('正在刷新账号列表...')
            self.account_table.setRowCount(0)
            
            accounts = self.account_manager.get_all_accounts()
            
            for row, account in enumerate(accounts):
                self.account_table.insertRow(row)
                
                # 使用字典格式访问账号信息
                username_item = QTableWidgetItem(account['username'])
                username_item.setFlags(username_item.flags() & ~Qt.ItemIsEditable)
                self.account_table.setItem(row, 0, username_item)
                
                # 最后登录时间
                last_login = account.get('last_login', '-')
                last_login_item = QTableWidgetItem(str(last_login))
                last_login_item.setFlags(last_login_item.flags() & ~Qt.ItemIsEditable)
                self.account_table.setItem(row, 1, last_login_item)
                
                # 状态
                status = account.get('status', '-')
                status_item = QTableWidgetItem(str(status))
                status_item.setFlags(status_item.flags() & ~Qt.ItemIsEditable)
                self.account_table.setItem(row, 2, status_item)
            
            self.status_label.setText('账号列表刷新完成')
            
        except Exception as e:
            self.logger.error(f"刷新账号列表出错: {str(e)}")
            self.status_label.setText('刷新账号列表失败')
            QMessageBox.critical(self, "错误", f"刷新账号列表失败: {str(e)}")
        
    def add_account(self):
        """添加账号"""
        try:
            self.status_label.setText('正在打开登录窗口...')
            
            # 打开登录窗口
            result = self.account_manager.session_manager.open_login_window()
            
            if result['success']:
                username = result['user_info'].get('name')
                if not username:
                    raise Exception("未能获取用户名")
                
                cookies = result['cookies']
                
                if self.account_manager.add_account(username, cookies):
                    QMessageBox.information(self, "成功", f"账号 {username} 添加成功！")
                    self.refresh_account_table()
                    self.status_label.setText('账号添加成功')
                else:
                    QMessageBox.warning(self, "失败", "添加账号失败，请重试")
                    self.status_label.setText('账号添加失败')
            else:
                QMessageBox.warning(self, "失败", f"登录失败: {result.get('error', '未知错误')}")
                self.status_label.setText('登录失败')
                
        except Exception as e:
            self.logger.error(f"添加账号时出错: {str(e)}")
            QMessageBox.critical(self, "错误", f"添加账号时出错: {str(e)}")
            self.status_label.setText('出错')
        finally:
            self.status_label.setText('就绪')
            
    def delete_account(self, username):
        """删除账号"""
        try:
            reply = QMessageBox.question(
                self, '确认删除', 
                f'确定要删除账号 {username} 吗？',
                QMessageBox.Yes | QMessageBox.No, 
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                if self.account_manager.remove_account(username):
                    self.refresh_account_table()
                    self.status_label.setText('账号删除成功')
                else:
                    QMessageBox.warning(self, "失败", "删除账号失败")
                    self.status_label.setText('账号删除失败')
                    
        except Exception as e:
            self.logger.error(f"删除账号时出错: {str(e)}")
            QMessageBox.critical(self, "错误", f"删除账号时出错: {str(e)}")
            self.status_label.setText('出错')
            
    def on_account_selected(self, index):
        """处理账号选择事件"""
        try:
            row = index.row()
            username = self.account_table.item(row, 0).text()
            self.refresh_article_table(username)
        except Exception as e:
            self.logger.error(f"处理账号选择事件出错: {str(e)}")
            
    def refresh_article_table(self, username):
        """刷新文章列表"""
        try:
            self.status_label.setText(f'正在获取 {username} 的文章列表...')
            self.article_table.setRowCount(0)
            
            # 获取特定账号的信息
            account = self.account_manager.get_account(username)
            if not account:
                raise Exception(f"找不到账号 {username}")
            
            cookies = account.get('cookies')  # 使用字典格式获取 cookies
            if not cookies:
                raise Exception(f"账号 {username} 的 cookies 无效")
            
            # 创建并启动获取线程
            self.fetch_thread = ArticleFetchThread(cookies)
            self.fetch_thread.finished.connect(self.update_article_table)
            self.fetch_thread.error.connect(self.handle_fetch_error)
            self.fetch_thread.start()
            
        except Exception as e:
            self.logger.error(f"刷新文章列表出错: {str(e)}")
            QMessageBox.critical(self, "错误", f"获取文章列表失败: {str(e)}")
            self.status_label.setText('获取文章列表失败')

    def update_article_table(self, articles):
        """更新文章表格"""
        try:
            self.article_table.setRowCount(0)
            
            for row, article in enumerate(articles):
                self.article_table.insertRow(row)
                
                # 标题
                title_item = QTableWidgetItem(article['title'])
                title_item.setFlags(title_item.flags() & ~Qt.ItemIsEditable)
                self.article_table.setItem(row, 0, title_item)
                
                # 发布时间
                time_item = QTableWidgetItem(article.get('publish_time', '-'))
                time_item.setFlags(time_item.flags() & ~Qt.ItemIsEditable)
                self.article_table.setItem(row, 1, time_item)
                
                # 点赞数
                digg_item = QTableWidgetItem(str(article.get('digg_count', 0)))
                digg_item.setFlags(digg_item.flags() & ~Qt.ItemIsEditable)
                self.article_table.setItem(row, 2, digg_item)
                
                # 展现量
                show_item = QTableWidgetItem(str(article.get('show_count', 0)))
                show_item.setFlags(show_item.flags() & ~Qt.ItemIsEditable)
                self.article_table.setItem(row, 3, show_item)
                
                # 阅读量
                read_item = QTableWidgetItem(str(article.get('read_count', 0)))
                read_item.setFlags(read_item.flags() & ~Qt.ItemIsEditable)
                self.article_table.setItem(row, 4, read_item)
                
                # 评论数
                comment_item = QTableWidgetItem(str(article.get('comment_count', 0)))
                comment_item.setFlags(comment_item.flags() & ~Qt.ItemIsEditable)
                self.article_table.setItem(row, 5, comment_item)
            
            self.status_label.setText('文章列表获取完成')
            
        except Exception as e:
            self.logger.error(f"更新文章表格出错: {str(e)}")
            QMessageBox.critical(self, "错误", f"更新文章列表失败: {str(e)}")
            self.status_label.setText('更新文章列表失败')

    def handle_fetch_error(self, error_msg):
        """处理获取错误"""
        self.logger.error(f"获取文章列表失败: {error_msg}")
        QMessageBox.critical(self, "错误", f"获取文章列表失败: {error_msg}")
        self.status_label.setText('获取文章列表失败')

    def refresh_all(self):
        """刷新所有数据"""
        self.refresh_account_table()
        
        # 如果有选中的账号，也刷新文章列表
        selected_items = self.account_table.selectedItems()
        if selected_items:
            username = self.account_table.item(selected_items[0].row(), 0).text()
            self.refresh_article_table(username)