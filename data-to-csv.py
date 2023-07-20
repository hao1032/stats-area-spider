import csv
import json
# 将 data.json 转成 data.csv 格式，方便导入数据库等用途，会转成以下格式

# area_id,parent_id,area_code,area_name,short_name,level,sort_num
# 11,0,11,北京市,北京市,1,1
# 110100000000,11,110100000000,市辖区,市辖区,2,1
# 110101000000,110100000000,110101000000,东城区,东城区,3,1
# 110101001000,110101000000,110101001000,东华门街道,东华门街道,4,1


def convert_to_csv(data, parent_id=0, level=1):
    csv_rows = []
    children = data.get('children', [])
    if level == 3:  # 打印区级信息，观察进度
        print(f'{data["name"]}, {len(children)}')
    for index, child in enumerate(children):
        # 某些只有市辖区的区去掉，类似 http://www.stats.gov.cn/sj/tjbz/tjyqhdmhcxhfdm/2022/34/3401.html
        if not child['url'] and child['name'] == '市辖区':
            continue
        area_id = child['code']
        area_code = child['code']
        area_name = child['name']
        short_name = child['name']
        sort_num = index + 1
        csv_rows.append([area_id, parent_id, area_code, area_name, short_name, level, sort_num])
        csv_rows.extend(convert_to_csv(child, area_id, level + 1))
    return csv_rows


with open('data.json', 'rb') as f:
    area_data = json.load(f)
    csv_data = convert_to_csv(area_data)

    # 写入CSV文件
    csv_file = 'area_data.csv'
    csv_headers = ['area_id', 'parent_id', 'area_code', 'area_name', 'short_name', 'level', 'sort_num']

    with open(csv_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(csv_headers)
        writer.writerows(csv_data)

    print(f"数据已成功转换并保存到 {csv_file} 文件中。")
