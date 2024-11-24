import pandas as pd

# 加载Excel文件路径
city_construction_file = 'data/original_all/city_construction_chn_year.xlsx'
city_data_file = 'data/original_all/city_data_year.xlsx'
gdp_file = 'data/original_all/gdp_chn_year_city(2000-2023).xlsx'
house_price_file = 'data/original_all/house_price_58_chn_year_city（2010-2024）.xlsx'

# 读取每个表格数据
city_construction_df = pd.read_excel(city_construction_file, engine='openpyxl')
city_data_df = pd.read_excel(city_data_file, engine='openpyxl')
gdp_df = pd.read_excel(gdp_file, engine='openpyxl')
house_price_df = pd.read_excel(house_price_file, engine='openpyxl')

# 清理列名，去除空格
for df in [city_construction_df, city_data_df, gdp_df, house_price_df]:
    df.columns = df.columns.str.strip()

# 预处理：统一城市名称，去掉“市”字
for df in [city_construction_df, city_data_df, gdp_df, house_price_df]:
    if '城市' in df.columns:
        df['城市'] = df['城市'].str.replace('市', '', regex=False)

# 将 "地区" 列重命名为 "城市"（如果存在）
if '地区' in city_construction_df.columns:
    city_construction_df.rename(columns={'地区': '城市'}, inplace=True)
if '地区' in city_data_df.columns:
    city_data_df.rename(columns={'地区': '城市'}, inplace=True)

# 预处理：统一年份为整数
for df in [city_construction_df, city_data_df, gdp_df, house_price_df]:
    if '年份' in df.columns:
        df['年份'] = df['年份'].astype(int)

# 检查每个表格的城市和年份范围
print("城市建设数据范围：", city_construction_df[['城市', '年份']].drop_duplicates())
print("城市人口数据范围：", city_data_df[['城市', '年份']].drop_duplicates())
print("GDP 数据范围：", gdp_df[['城市', '年份']].drop_duplicates())
print("房价数据范围：", house_price_df[['省份', '城市', '年份']].drop_duplicates())

# 合并城市建设数据与城市人口数据
merged_df = pd.merge(
    city_construction_df[['城市', '年份', '市区面积_平方公里', '建成区面积_平方公里']],
    city_data_df[['城市', '年份', '户籍人口(万人)']],
    on=['城市', '年份'],
    how='inner'
)

# 合并 GDP 数据
merged_df = pd.merge(
    merged_df,
    gdp_df.drop(columns=['GDP平减指数']),  # 删除 GDP 数据中的“GDP平减指数”列
    on=['城市', '年份'],
    how='inner'
)

# 合并房价数据，忽略省份字段
merged_df = pd.merge(
    merged_df,
    house_price_df[['城市', '年份', '价格']],  # 房价数据只需要 "价格" 列
    on=['城市', '年份'],
    how='inner'
)

# 调整列顺序
columns_order = ['省份', '城市', '年份', '价格', '实际GDP', '名义GDP', 'GDP指数',
                 '市区面积_平方公里', '建成区面积_平方公里', '户籍人口(万人)']
merged_df = merged_df[columns_order]

# 打印调整后的列名
print("调整列顺序后数据的列名：", merged_df.columns.tolist())

# 保存结果到文件
output_file = 'data/unprocessed_chn_year_data.xlsx'
merged_df.to_excel(output_file, index=False)
print(f"调整列顺序后的合并结果保存到 {output_file}")
