import pandas as pd

# 文件路径
file_path = 'data/unprocessed_chn_year_data.xlsx'
output_file_path = 'data/processed_chn_year_data.xlsx'
city_years_output = 'data/city_years_statistics.xlsx'

# 读取数据
data = pd.read_excel(file_path)

# 缺失值情况统计
print("\n缺失值统计：")
print(data.isnull().sum())

# 每个城市的数据年份统计（年份列汇总）
print("\n每个城市包含的年份列表：")
city_years = data.groupby('城市')['年份'].apply(list).reset_index()
print(city_years)

# 保存城市年份统计到表格
city_years.to_excel(city_years_output, index=False)
print(f"\n每个城市的年份统计已保存到 {city_years_output}")

# 处理价格列，将单位移至列名
if '价格' in data.columns:
    data.rename(columns={'价格': '价格（元/㎡）'}, inplace=True)
    # 将价格列中带有 "元/㎡" 的单位移除
    data['价格（元/㎡）'] = data['价格（元/㎡）'].replace(r'元/㎡', '', regex=True).astype(float)

# 基础数据预处理
# 按城市和年份排序
data = data.sort_values(by=['城市', '年份'])

# 补充缺失值（线性插值）
data = data.interpolate(method='linear')

# 去重
data = data.drop_duplicates()

# 打印处理后的信息
print("\n处理后的数据基本信息：")
print(data.info())

print("\n处理后的缺失值统计：")
print(data.isnull().sum())

# 保存处理后的数据
data.to_excel(output_file_path, index=False)
print(f"\n处理后的数据已保存到 {output_file_path}")
