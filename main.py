import re
import json
import time

import requests
from bs4 import BeautifulSoup


class Main(object):
    def __init__(self):
        self.data = None

    def request(self, url):
        print(f'请求: {url}')
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'
        }
        try:
            resp = requests.get(url, headers=headers, timeout=5)
            resp.encoding = 'utf-8'
        except requests.exceptions.RequestException as e:
            print(f'error: {e}')
            return '<html></html>'  # 遇到错误返回空，没有结果，不会标记 finish，后面还会再次抓取
        return resp.text

    def get_children_province(self, bs, url):
        """
        获取省级数据，省级数据和其下级数据表现方式不一样
        :param bs:
        :param url:
        :return:
        """
        base_url = url.replace('index.html', '')
        links = bs.find_all('a', href=re.compile('html'))
        children = []
        for link in links:
            child = {
                'code': link['href'].replace('.html', '').strip(),
                'name': link.get_text().strip(),
                'url': f'{base_url}{link["href"]}',
                'status': "start",  # 标记尚未抓取下级区域
                'children': []
            }
            children.append(child)
        return children

    def get_children_not_province(self, bs, url):
        """
        获取非省级数据，通过 class name 找到对应的数据
        :param bs:
        :param url:
        :return:
        """
        base_url = url[0: url.rfind('/') + 1]
        table_trs = bs.find_all('tr', class_='citytr')           # 市级
        table_trs.extend(bs.find_all('tr', class_='countytr'))   # 区级
        table_trs.extend(bs.find_all('tr', class_='towntr'))     # 镇级
        table_trs.extend(bs.find_all('tr', class_='villagetr'))  # 村级
        children = []
        for tr in table_trs:
            link = tr.find('a')
            table_tds = tr.find_all('td')
            url = f'{base_url}{link["href"]}' if link else ''  # 村级和某些区级没有链接
            child = {
                'code': table_tds[0].get_text().strip(),
                'name': table_tds[-1].get_text().strip(),  # 省市区镇有 2 列，村有 3 列，使用 -1 获取名称
                'url': url,
                'status': "start" if url else 'finish',  # 如果没有链接，标记完成
                'children': []
            }
            children.append(child)
        return children

    def get_children(self, url):
        html = self.request(url)
        # time.sleep(1)  # 防止请求过快
        bs = BeautifulSoup(html, 'lxml')
        is_index = 'index.html' in url  # 判断是否主页，主页需要获取省份和非省份规则不同
        children = self.get_children_province(bs, url) if is_index else self.get_children_not_province(bs, url)
        return children

    def handle_node(self, node):
        children = self.get_children(node['url'])
        print(node['name'], len(children))
        if children:
            node['children-size'] = len(children)
            node['children'] = children
            node['status'] = 'finish'  # 标记抓取完成

    def find_start_node(self, data):
        """
        通过递归找到一个尚未抓取的 node
        :param data:
        :return:
        """
        if isinstance(data, dict):
            if data['status'] == 'start':
                return data
            result = self.find_start_node(data['children'])
            if result:
                return result
        elif isinstance(data, list):
            for item in data:
                result = self.find_start_node(item)
                if result:
                    return result
        return None

    def save_data_file(self):
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    def run(self):
        # 加载当前已有数据
        with open('data.json', 'rb') as f:
            self.data = json.load(f)

        # 通过循环抓取尚未完成的数据
        start_time = time.time()
        while True:
            node = self.find_start_node(self.data)
            if node:
                # 抓取一个 node 后，保存数据
                self.handle_node(node)
            else:
                break

            # 每隔一段时间保存一次，5 分钟
            if time.time() - start_time > 5 * 60:
                self.save_data_file()
                start_time = time.time()


Main().run()
