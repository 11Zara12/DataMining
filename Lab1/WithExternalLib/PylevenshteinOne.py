import pandas as pd
import Levenshtein
import time
import re

"""
sheet1:第一列序号，第二列期刊名称，第三列影响因子
sheet2:包含期刊名和对应的简称(个数不定)，数据从第一列就有
sheet3:第一列全名，第二列影响因子，第三列及后为期刊可能的简称
(按照期刊全名字母序排列)

注意：sheet1中和sheet2中期刊列表来源不一致，有不相重叠的部分，也有部分期刊名字写法不一致，
如可能多个逗号，可能把and写成&等，也有部分期刊名字相似但并非同一期刊。
"""

"""--------------------------------------------数据预处理--------------------------------------------"""

# 加载Excel文件
file_path = 'Lab1.xlsx'
xls = pd.ExcelFile(file_path)

# 读取sheet1和sheet2
sheet1 = xls.parse('sheet1')
sheet2 = xls.parse('sheet2')

# 清理sheet1的数据
sheet1 = sheet1.rename(columns={sheet1.columns[1]: 'Journal Name', sheet1.columns[2]: 'Impact Factor'})
sheet1 = sheet1[['Journal Name', 'Impact Factor']].dropna()  # 删除缺失值

# 清理sheet2的数据
sheet2.columns = ['Journal Name'] + [f'Abbreviation_{i}' for i in range(1, len(sheet2.columns))]  # 设置列名
sheet2 = sheet2.dropna(how='all', axis=1)  # 删除完全为空的列

# 期刊名标准化（转换为小写并去除空格和替换符号）
def normalize_journal_name(name):
    name = name.lower().strip()  # 转小写并去除前后空格
    name = re.sub(r'[-,()&]', ' ', name)  # 替换符号为单个空格
    name = name.replace('and', '&')  # 替换"and"为"&"
    return name

# 应用标准化处理
sheet1['Journal Name Lower'] = sheet1['Journal Name'].apply(normalize_journal_name)
sheet2['Journal Name Lower'] = sheet2['Journal Name'].apply(normalize_journal_name)

# 找出sheet1和sheet2中不匹配的期刊名
names_in_sheet1 = set(sheet1['Journal Name Lower'])  # sheet1中的期刊名集合
names_in_sheet2 = set(sheet2['Journal Name Lower'])  # sheet2中的期刊名集合

only_in_sheet1 = names_in_sheet1 - names_in_sheet2  # 仅在sheet1中出现的期刊
only_in_sheet2 = names_in_sheet2 - names_in_sheet1  # 仅在sheet2中出现的期刊


# 记录匹配开始时间
start_time = time.time()

"""----------------------------使用Levenshtein距离进行期刊名匹配---------------------------------------"""

matched_names = []
for name1 in only_in_sheet1:
    best_match = None
    best_score = float('inf')  # 初始化一个最小的编辑距离
    for name2 in only_in_sheet2:
        score = Levenshtein.distance(name1, name2)  # 计算两个名字之间的Levenshtein距离
        if score < best_score:  # 找到更好的匹配
            best_score = score
            best_match = name2
    if best_match and best_score < 5:  # 阈值设置为5
        matched_names.append((name1, best_match))  # 将匹配的期刊名添加到列表中

# 创建一个包含匹配期刊名的DataFrame
matched_df = pd.DataFrame(matched_names, columns=['Sheet1 Name', 'Sheet2 Closest Match'])

# 将匹配的期刊名回填到原始数据中
sheet1['Matched Name'] = sheet1['Journal Name Lower']  # 默认将'Journal Name Lower'作为'Matched Name'
sheet2['Matched Name'] = sheet2['Journal Name Lower']  # 默认将'Journal Name Lower'作为'Matched Name'

# 将匹配到的期刊名更新到sheet1和sheet2中
for index, row in matched_df.iterrows():
    sheet1.loc[sheet1['Journal Name Lower'] == row['Sheet1 Name'], 'Matched Name'] = row['Sheet2 Closest Match']
    sheet2.loc[sheet2['Journal Name Lower'] == row['Sheet2 Closest Match'], 'Matched Name'] = row['Sheet2 Closest Match']

# 根据匹配的期刊名合并sheet1和sheet2
merged_data = pd.merge(
    sheet1, sheet2, how='outer', left_on='Matched Name', right_on='Matched Name'  # 使用'Matched Name'作为连接键
).sort_values(by=['Journal Name_x'])  # 按照'Journal Name_x'排序

# 准备最终输出的结果
final_output = merged_data[
    ['Journal Name_x', 'Impact Factor', 'Abbreviation_1', 'Abbreviation_2', 'Abbreviation_3']
].rename(columns={
    'Journal Name_x': 'Journal Name',  # 重命名'Journal Name_x'为'Journal Name'
    'Impact Factor': 'Impact Factor',
})

# 记录匹配操作结束时间
end_time = time.time()

# 将结果保存为新的Excel文件
output_path = './OutputsForE/sheet3_with_pyL.xlsx'
with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
    final_output.to_excel(writer, sheet_name='sheet3', index=False)  # 将最终结果写入'sheet3'工作表

# 打印匹配操作所需的时间
print(f"Matching operation time: {end_time - start_time:.2f} seconds")
