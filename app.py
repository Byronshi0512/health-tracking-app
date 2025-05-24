import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import json
import os

# 页面配置
st.set_page_config(
    page_title="个人健康数据追踪",
    page_icon="🏃",
    layout="wide"
)

# 初始化会话状态
if 'health_data' not in st.session_state:
    if os.path.exists('health_data.json'):
        with open('health_data.json', 'r') as f:
            st.session_state.health_data = json.load(f)
    else:
        st.session_state.health_data = {
            'weight': [],
            'exercise': [],
            'sleep': [],
            'mood': []
        }

# 侧边栏
st.sidebar.title("导航")
page = st.sidebar.radio("选择页面", ["数据输入", "数据可视化", "数据统计"])

# 数据输入页面
if page == "数据输入":
    st.title("健康数据记录")
    
    # 创建两列布局
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("体重记录")
        weight = st.number_input("今日体重 (kg)", min_value=0.0, max_value=300.0, step=0.1)
        if st.button("记录体重"):
            st.session_state.health_data['weight'].append({
                'date': datetime.now().strftime('%Y-%m-%d'),
                'value': weight
            })
            st.success("体重记录已保存！")
    
    with col2:
        st.subheader("运动记录")
        exercise_type = st.selectbox("运动类型", ["跑步", "游泳", "骑行", "健身", "其他"])
        duration = st.number_input("运动时长 (分钟)", min_value=0, max_value=300)
        if st.button("记录运动"):
            st.session_state.health_data['exercise'].append({
                'date': datetime.now().strftime('%Y-%m-%d'),
                'type': exercise_type,
                'duration': duration
            })
            st.success("运动记录已保存！")
    
    # 睡眠和心情记录
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("睡眠记录")
        sleep_hours = st.number_input("睡眠时长 (小时)", min_value=0.0, max_value=24.0, step=0.5)
        sleep_quality = st.slider("睡眠质量", 1, 10, 7)
        if st.button("记录睡眠"):
            st.session_state.health_data['sleep'].append({
                'date': datetime.now().strftime('%Y-%m-%d'),
                'hours': sleep_hours,
                'quality': sleep_quality
            })
            st.success("睡眠记录已保存！")
    
    with col4:
        st.subheader("心情记录")
        mood = st.select_slider("今日心情", 
                              options=["😢 很差", "😕 一般", "😊 不错", "😄 很好", "🤩 极好"])
        if st.button("记录心情"):
            st.session_state.health_data['mood'].append({
                'date': datetime.now().strftime('%Y-%m-%d'),
                'value': mood
            })
            st.success("心情记录已保存！")

# 数据可视化页面
elif page == "数据可视化":
    st.title("健康数据可视化")
    
    # 将数据转换为DataFrame
    weight_df = pd.DataFrame(st.session_state.health_data['weight'])
    exercise_df = pd.DataFrame(st.session_state.health_data['exercise'])
    sleep_df = pd.DataFrame(st.session_state.health_data['sleep'])
    mood_df = pd.DataFrame(st.session_state.health_data['mood'])
    
    # 创建图表
    if not weight_df.empty:
        st.subheader("体重趋势")
        fig_weight = px.line(weight_df, x='date', y='value', title='体重变化趋势')
        st.plotly_chart(fig_weight)
    
    if not exercise_df.empty:
        st.subheader("运动记录")
        fig_exercise = px.bar(exercise_df, x='date', y='duration', color='type',
                            title='运动时长统计')
        st.plotly_chart(fig_exercise)
    
    if not sleep_df.empty:
        st.subheader("睡眠质量")
        fig_sleep = px.scatter(sleep_df, x='hours', y='quality', title='睡眠时长与质量关系')
        st.plotly_chart(fig_sleep)

# 数据统计页面
else:
    st.title("数据统计")
    
    # 计算基本统计数据
    if st.session_state.health_data['weight']:
        weights = [w['value'] for w in st.session_state.health_data['weight']]
        st.metric("平均体重", f"{sum(weights)/len(weights):.1f} kg")
    
    if st.session_state.health_data['exercise']:
        total_exercise = sum(e['duration'] for e in st.session_state.health_data['exercise'])
        st.metric("总运动时长", f"{total_exercise} 分钟")
    
    if st.session_state.health_data['sleep']:
        avg_sleep = sum(s['hours'] for s in st.session_state.health_data['sleep'])/len(st.session_state.health_data['sleep'])
        st.metric("平均睡眠时长", f"{avg_sleep:.1f} 小时")

# 保存数据
with open('health_data.json', 'w') as f:
    json.dump(st.session_state.health_data, f) 