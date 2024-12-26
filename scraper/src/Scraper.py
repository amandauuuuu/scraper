import requests
import csv
from bs4 import BeautifulSoup
import os

# 检查当前工作目录
print("当前工作目录:", os.getcwd())

# 请求下载网页
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
}

# 禁用 SSL 验证
page = requests.get('the website address you want to scrap', headers=headers, verify=False)

# 解析 HTML 内容
soup = BeautifulSoup(page.text, 'html.parser')

def extract_authors(soup):
    authors = []
    td_tags = soup.find_all('td')
    for td in td_tags:
        author_info = td.text.strip()
        if ',' in author_info:  # 检查是否有多个作者
            author_list = [author.strip() for author in author_info.split(',')]
            authors.append(author_list)
    
    print(f"在此页面找到 {len(authors)} 个作者。")
    return authors

def get_next_page_url(soup):
    """
    检查是否有下一页并返回相对 URL。
    如果没有下一页，则返回 None。
    """
    next_page_link = soup.find('a', title="Go to next page")
    if next_page_link:
        return next_page_link.get('href')  # 返回相对 URL
    return None

def crawl_website(start_url):
    """
    从给定的 URL 开始爬取网站，直到没有下一页为止。
    """
    base_url = "https://www.usenix.org"  # 基础 URL 用于拼接相对 URL
    current_url = start_url
    all_authors = []  # 这个列表将存储所有页面的作者数据

    while current_url:
        print(f"正在爬取 {current_url}...")

        # 爬取当前页面并禁用 SSL 验证
        response = requests.get(current_url, verify=False)  # 禁用 SSL 验证
        soup = BeautifulSoup(response.text, 'html.parser')

        # 处理页面内容（例如提取作者）
        authors = extract_authors(soup)
        print(f"从此页面提取了 {len(authors)} 个作者。")

        # 将作者添加到 all_authors 列表中
        all_authors.extend(authors)

        # 查找下一页的 URL
        next_page_relative_url = get_next_page_url(soup)
        if next_page_relative_url:
            # 构造下一页的完整 URL
            current_url = base_url + next_page_relative_url
        else:
            # 没有找到下一页，停止循环
            print("没有更多页面可爬取。")
            current_url = None  # 结束循环

    # 在循环结束后，将所有提取的作者保存到 CSV 文件
    save_to_csv(all_authors)  # 保存数据到 CSV 文件

def save_to_csv(authors, filename="authors.csv"):
    """
    将提取的作者数据保存到 CSV 文件中。
    """
    if authors:
        # 扁平化作者列表（不再使用 'author1', 'author2' 键，只存储作者名称）
        flat_authors = [author for sublist in authors for author in sublist]
        
        # 写入 CSV 文件
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)  # 使用 csv.writer 而不是 DictWriter
            writer.writerow(['Author'])  # 写入仅有一个列名 "Author" 的标题行
            
            # 将每个作者名称写入 CSV 文件
            for author in flat_authors:
                writer.writerow([author])
        
        print(f"数据已保存到 {filename}")
    else:
        print("没有作者数据需要保存。")

# 从第一页开始爬取
start_url = "https://www.usenix.org/publications/proceedings/osdi"
crawl_website(start_url)
