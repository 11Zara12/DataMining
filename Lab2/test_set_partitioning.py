import pandas as pd

# 加载数据文件
file_path = 'data/original_all/house_price_58_chn_year_city（2010-2024）.xlsx'
data = pd.ExcelFile(file_path)


df = data.parse('Sheet1')

# 将年份列转换为数值类型
df['年份'] = pd.to_numeric(df['年份'], errors='coerce')

# 移除“价格”列中的“元/㎡”，并转换为数值类型
df['价格'] = df['价格'].str.replace('元/㎡', '', regex=False).str.replace(',', '').astype(float)

# 修改列名，将单位添加到列名中
df.rename(columns={'价格': '价格（元/㎡）'}, inplace=True)

# 筛选2023年和2024年的数据作为测试集
test_data = df[df['年份'].isin([2023, 2024])]

# 筛选指定城市的数据：佛山、北京、成都、无锡、武汉、济南、石家庄、苏州、重庆、青岛、三亚
selected_cities = ['佛山', '北京', '成都', '无锡', '武汉', '济南', '石家庄', '苏州', '重庆', '青岛', '三亚']
selected_cities_data = test_data[test_data['城市'].isin(selected_cities)]

# 输出筛选结果，只显示前四列
print(selected_cities_data.iloc[:, :4])

# 将筛选后的结果保存到Excel文件
output_file_path = 'data/2023_2024_selected_cities_data_cleaned.xlsx'
selected_cities_data.iloc[:, :4].to_excel(output_file_path, index=False, sheet_name='Top5_Columns')
print(f"筛选结果（前四列）已保存到: {output_file_path}")
