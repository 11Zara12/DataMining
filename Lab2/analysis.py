import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from mpl_toolkits.mplot3d import Axes3D
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np

# Matplotlib设置
plt.rcParams['font.sans-serif'] = ['SimHei']  # 黑体
plt.rcParams['axes.unicode_minus'] = False  # 正常显示负号

# 文件路径
processed_file_path = 'data/processed_chn_year_data.xlsx'
city_years_file_path = 'data/city_years_statistics.xlsx'

# 加载数据
processed_data = pd.read_excel(processed_file_path)
city_years_data = pd.read_excel(city_years_file_path)

"""-------------------Task 1: 房价与其他特征的相关性分析---------------------"""
numerical_columns = ['价格（元/㎡）', '实际GDP', '名义GDP', 'GDP指数', '市区面积_平方公里', '建成区面积_平方公里', '户籍人口(万人)']
correlation_matrix = processed_data[numerical_columns].corr()

plt.figure(figsize=(10, 8))
sns.heatmap(correlation_matrix, annot=True, fmt='.2f', cmap='coolwarm', cbar=True)
plt.title('房价与其他特征的相关性矩阵')
plt.show()

"""-------------------Task 2: 长期房价趋势与经济变化分析---------------------"""
city_years_data['YearCount'] = city_years_data['年份'].apply(lambda x: len(eval(x)) if isinstance(x, str) else 0)
city_years_data['年份'] = city_years_data['年份'].apply(eval)
top_cities = city_years_data.sort_values(by='YearCount', ascending=False).head(10)

print("选择的十个城市及其年份：")
print(top_cities[['城市', '年份']])

filtered_data = processed_data[processed_data['城市'].isin(top_cities['城市'])]
grouped_data = filtered_data.groupby(['城市', '年份']).agg({'价格（元/㎡）': 'mean', '实际GDP': 'mean'}).reset_index()

"""功能 1：使用 3D 图展示十个选中城市的房价走势对比"""
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')
for city in top_cities['城市']:
    city_data = grouped_data[grouped_data['城市'] == city]
    ax.plot(city_data['年份'], city_data['价格（元/㎡）'], zs=top_cities[top_cities['城市'] == city].index[0], zdir='y', label=city)

ax.set_title('十个城市的房价走势对比')
ax.set_xlabel('年份')
ax.set_ylabel('城市索引')
ax.set_zlabel('房价（元/㎡）')
ax.legend()
plt.show()

# 单独展示各城市走势
for city in top_cities['城市']:
    city_data = grouped_data[grouped_data['城市'] == city].sort_values(by='年份')
    plt.figure(figsize=(10, 6))
    plt.plot(city_data['年份'], city_data['价格（元/㎡）'], label='房价（元/㎡）', marker='o')
    plt.plot(city_data['年份'], city_data['实际GDP'], label='实际GDP', marker='x')
    plt.title(f'{city} - 房价与实际GDP的长期变化趋势')
    plt.xlabel('年份')
    plt.ylabel('值')
    plt.legend()
    plt.grid(True)
    plt.show()

"""-------------------Task 3: 房价与经济变化的滞后/提前关系分析---------------------"""
def analyze_price_economic_relationship(data, city_col='城市', year_col='年份', price_col='价格（元/㎡）', economic_col='实际GDP'):
    results = []
    for city in data[city_col].unique():
        city_data = data[data[city_col] == city].sort_values(by=year_col)
        if len(city_data) > 2:  # 至少需要两个年份的数据
            lags = range(-3, 4)
            max_corr = -1
            best_lag = 0

            for lag in lags:
                shifted_economic = city_data[economic_col].shift(lag).dropna()
                shifted_price = city_data[price_col].iloc[max(0, lag):].reset_index(drop=True)
                min_length = min(len(shifted_economic), len(shifted_price))
                if min_length > 1:
                    corr = np.corrcoef(shifted_economic[:min_length], shifted_price[:min_length])[0, 1]
                    if corr > max_corr:
                        max_corr = corr
                        best_lag = lag

            relationship = "同步" if best_lag == 0 else ("提前" if best_lag > 0 else "滞后")
            results.append({'城市': city, '最优滞后时间（年）': best_lag, '关系': relationship, '最大相关系数': max_corr})

    return pd.DataFrame(results)

relationship_results = analyze_price_economic_relationship(grouped_data)
print("房价与经济变化滞后/提前关系分析：")
print(relationship_results)

"""-------------------Task 4: 房价预测---------------------"""
def predict_future_prices(data, target_col='价格（元/㎡）', future_year=2025, group_col=None):
    predictions = []
    errors = []
    r2_scores = []

    if group_col and group_col in data.columns:
        groups = data[group_col].unique()
        for group in groups:
            group_data = data[data[group_col] == group].sort_values(by='年份')
            if len(group_data) >= 2:  # 至少需要两个年份的数据
                X = group_data[['年份']].values
                y = group_data[target_col].values

                model = LinearRegression()
                model.fit(X, y)
                predicted_price = model.predict([[future_year]])

                # 模型评估
                y_pred = model.predict(X)
                mae = mean_absolute_error(y, y_pred)
                mse = mean_squared_error(y, y_pred)
                rmse = np.sqrt(mse)
                r2 = r2_score(y, y_pred)
                predictions.append({group_col: group, f'预测房价({future_year}年)（元/㎡）': predicted_price[0]})
                errors.append({'城市': group, 'MAE': mae, 'MSE': mse, 'RMSE': rmse, 'R²': r2})

    else:
        if len(data) >= 2:  # 对整体数据进行预测
            X = data[['年份']].values
            y = data[target_col].values

            model = LinearRegression()
            model.fit(X, y)
            predicted_price = model.predict([[future_year]])

            # 模型评估
            y_pred = model.predict(X)
            mae = mean_absolute_error(y, y_pred)
            mse = mean_squared_error(y, y_pred)
            rmse = np.sqrt(mse)
            r2 = r2_score(y, y_pred)
            predictions.append({f'预测房价({future_year}年)（元/㎡）': predicted_price[0]})
            errors.append({'城市': '整体', 'MAE': mae, 'MSE': mse, 'RMSE': rmse, 'R²': r2})

    predictions_df = pd.DataFrame(predictions)
    errors_df = pd.DataFrame(errors)
    return predictions_df, errors_df

# 房价预测与模型评估
predictions, errors = predict_future_prices(grouped_data, target_col='价格（元/㎡）', future_year=2025, group_col='城市')

print("预测结果：")
print(predictions)
print("\n模型误差：")
print(errors)

# 可视化预测结果
plt.figure(figsize=(12, 6))
sns.barplot(data=predictions, x='城市', y=f'预测房价(2025年)（元/㎡）', dodge=False, palette='Set2')
plt.title("2025年各城市预测房价")
plt.ylabel("预测房价（元/㎡）")
plt.xlabel("城市")
plt.xticks(rotation=45)
plt.grid(axis='y')
plt.legend([], [], frameon=False)  # 隐藏多余图例
plt.show()

"""功能 2：单独预测三亚的房价"""
# 三亚市的房价预测
sanya_data = processed_data[processed_data['城市'] == '三亚']
sanya_grouped = sanya_data.groupby(['年份']).agg({'价格（元/㎡）': 'mean'}).reset_index()

sanya_predictions, sanya_errors = predict_future_prices(
    sanya_grouped, target_col='价格（元/㎡）', future_year=2025, group_col=None
)

print("三亚房价预测：")
print(sanya_predictions)
print("\n三亚房价模型误差：")
print(sanya_errors)

# 三亚市预测可视化
plt.figure(figsize=(10, 6))
plt.plot(sanya_grouped['年份'], sanya_grouped['价格（元/㎡）'], marker='o', label='历史房价')
if not sanya_predictions.empty:
    plt.scatter(2025, sanya_predictions.iloc[0, 0], color='red', label=f'2025预测: {sanya_predictions.iloc[0, 0]:.2f}')
plt.title('三亚房价历史与预测')
plt.xlabel('年份')
plt.ylabel('价格（元/㎡）')
plt.legend()
plt.grid(True)
plt.show()

