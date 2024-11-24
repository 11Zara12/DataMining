from rapidfuzz import process, fuzz  # 导入 rapidfuzz 模块，用于快速字符串相似性计算
import pandas as pd

# 读取数据
sheet1_path = "Lab1.xlsx"
sheet1 = pd.read_excel(sheet1_path, sheet_name='sheet1')
sheet2 = pd.read_excel(sheet1_path, sheet_name='sheet2')

# 修正列名
sheet1.columns = ['ID', 'Journal_Name', 'Impact_Factor']  # sheet1 包含期刊编号、全名、影响因子
sheet2.columns = ['Journal_Name', 'Abbreviation_1', 'Abbreviation_2', 'Abbreviation_3']  # sheet2 包含期刊全名和简称

# 数据预处理：统一名称格式（去除多余空格并转为小写）
sheet1['Journal_Name'] = sheet1['Journal_Name'].str.strip().str.lower()
sheet2['Journal_Name'] = sheet2['Journal_Name'].str.strip().str.lower()

# 删除空值或无效值
sheet1 = sheet1.dropna(subset=['Journal_Name'])
sheet2 = sheet2.dropna(subset=['Journal_Name'])

# 不一致性分析
inconsistencies = []  # 用于存储不一致的结果

# 遍历 sheet1 中的每个期刊名称
for name1 in sheet1['Journal_Name']:
    # 使用 rapidfuzz 找出与当前期刊名称最匹配的名称
    match = process.extractOne(
        name1,  # 要匹配的目标名称（来自 sheet1）
        sheet2['Journal_Name'],  # 匹配的候选名称列表（来自 sheet2）
        scorer=fuzz.ratio  # 使用 fuzz.ratio 算法计算字符串相似度
    )
    if match:  # 如果找到匹配
        best_match, best_score, _ = match
        if best_score < 100:  # 如果匹配的相似度小于 100（表示不完全一致）
            # 记录不一致的结果
            inconsistencies.append((name1, best_match, best_score))
    else:
        # 如果没有找到任何匹配，记录为无匹配项
        inconsistencies.append((name1, "No Match Found", 0))

# 将不一致结果存储为 DataFrame
inconsistencies_df = pd.DataFrame(
    inconsistencies,
    columns=['Sheet1_Name', 'Sheet2_Potential_Match', 'Similarity']  # 定义列名
)

# 将结果保存到 Excel 文件中
output_path = "Inconsistencies_Analysis.xlsx"
inconsistencies_df.to_excel(output_path, index=False)  # 保存为文件，不包含索引

# 运行检测
print(f"不一致结果已保存到: {output_path}")
