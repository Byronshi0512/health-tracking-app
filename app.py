import streamlit as st
import json
from datetime import datetime

def load_data():
    try:
        with open('health_data.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_data(data):
    with open('health_data.json', 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def main():
    st.title("健康数据追踪")
    st.write("欢迎使用健康数据追踪应用！")
    
    # 加载现有数据
    health_data = load_data()
    
    # 侧边栏 - 数据输入
    with st.sidebar:
        st.header("记录健康数据")
        date = st.date_input("日期", datetime.now())
        weight = st.number_input("体重 (kg)", min_value=0.0, max_value=300.0, step=0.1)
        steps = st.number_input("步数", min_value=0, step=100)
        sleep_hours = st.number_input("睡眠时间 (小时)", min_value=0.0, max_value=24.0, step=0.5)
        
        if st.button("保存数据"):
            new_record = {
                "date": date.strftime("%Y-%m-%d"),
                "weight": weight,
                "steps": steps,
                "sleep_hours": sleep_hours
            }
            health_data.append(new_record)
            save_data(health_data)
            st.success("数据已保存！")
    
    # 主页面 - 数据显示
    st.header("历史记录")
    if health_data:
        for record in reversed(health_data):
            with st.expander(f"📅 {record['date']}"):
                st.write(f"体重: {record['weight']} kg")
                st.write(f"步数: {record['steps']} 步")
                st.write(f"睡眠时间: {record['sleep_hours']} 小时")
    else:
        st.info("还没有记录任何数据。请在左侧输入您的健康数据。")

if __name__ == "__main__":
    main() 