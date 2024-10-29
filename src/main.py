import sys
import logging
from PyQt5.QtWidgets import QApplication
from ui.account_manager_ui import AccountManagerUI

def setup_logging():
    """配置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),  # 输出到控制台
            logging.FileHandler('app.log', encoding='utf-8')  # 输出到文件
        ]
    )

def main():
    """主函数"""
    try:
        # 设置日志
        setup_logging()
        logger = logging.getLogger(__name__)
        logger.info("启动应用程序")
        
        # 创建应用
        app = QApplication(sys.argv)
        
        # 创建主窗口
        window = AccountManagerUI()
        window.show()
        
        # 运行应用
        sys.exit(app.exec_())
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"应用程序出错: {str(e)}")
        raise

if __name__ == '__main__':
    main()