# stats-area-spider
中国国家统计局行政区划代码爬虫

## 使用方式
1. 安装依赖包

`pip install -r requirements.txt`

依赖的库 `requests` `beautifulsoup4` `lxml`

2. 修改 data.json

如果是首次执行，且 data.json 有问题，需要修改文件内容为

```json
{
    "code": 0,
    "name": "root",
    "url": "http://www.stats.gov.cn/sj/tjbz/tjyqhdmhcxhfdm/2022/index.html",
    "status": "start",
    "children": []
}

字段说明：
code     区划代码
name     区划名称
url      当前区域对应的页面地址
status   爬虫状态标记 start【尚未抓取】 finish【抓取完成】
children 下级区域列表
```

如果是执行中途中断，不用修改改文件，重新执行脚本会按照当前进度继续抓取。

3. 执行脚本