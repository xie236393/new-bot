import os
from bs4 import BeautifulSoup

def analyze_page_structure():
    """分析保存的页面结构"""
    try:
        with open('page_source.html', 'r', encoding='utf-8') as f:
            html = f.read()
            
        soup = BeautifulSoup(html, 'html.parser')
        
        # 查找所有可能的文章元素
        article_elements = soup.find_all(class_=lambda x: x and 'article' in x.lower())
        
        print(f"找到 {len(article_elements)} 个可能的文章元素")
        
        # 分析第一个文章元素的结构
        if article_elements:
            first_article = article_elements[0]
            print("\n第一个文章元素的结构:")
            print(first_article.prettify())
            
            # 分析类名
            print("\n所有文章元素的类名:")
            class_names = set()
            for elem in article_elements:
                if elem.get('class'):
                    class_names.update(elem['class'])
            for class_name in sorted(class_names):
                print(f"- {class_name}")
            
    except Exception as e:
        print(f"分析页面失败: {e}")

if __name__ == '__main__':
    analyze_page_structure() 