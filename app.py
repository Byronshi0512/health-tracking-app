import streamlit as st
import json
from datetime import datetime
import plotly.express as px
import pandas as pd
import os
import shutil
from pathlib import Path
import fcntl

# 定义数据文件路径
DATA_DIR = Path.home() / '.health_tracker'
DATA_FILE = DATA_DIR / 'health_data.json'
BACKUP_FILE = DATA_DIR / 'health_data.backup.json'

def ensure_data_dir():
    """确保数据目录存在"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

def create_backup():
    """创建数据文件的备份"""
    if DATA_FILE.exists():
        shutil.copy2(DATA_FILE, BACKUP_FILE)

def load_data():
    """加载数据，包含错误处理和恢复机制"""
    ensure_data_dir()
    
    try:
        if DATA_FILE.exists():
            with open(DATA_FILE, 'r') as f:
                try:
                    fcntl.flock(f.fileno(), fcntl.LOCK_SH)
                    data = json.load(f)
                    # 确保数据按日期排序
                    data.sort(key=lambda x: x['date'], reverse=True)
                    return data
                except json.JSONDecodeError:
                    # 如果主文件损坏，尝试从备份恢复
                    if BACKUP_FILE.exists():
                        st.warning("主数据文件损坏，正在从备份恢复...")
                        with open(BACKUP_FILE, 'r') as backup:
                            data = json.load(backup)
                            save_data(data)  # 恢复主文件
                            return data
                    return []
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        return []
    except Exception as e:
        st.error(f"加载数据时出错: {str(e)}")
        return []

def save_data(data):
    """保存数据，包含错误处理和备份机制"""
    ensure_data_dir()
    
    # 创建备份
    create_backup()
    
    try:
        # 保存前先排序
        data.sort(key=lambda x: x['date'], reverse=True)
        
        # 使用临时文件进行原子写入
        temp_file = DATA_FILE.with_suffix('.tmp')
        with open(temp_file, 'w') as f:
            try:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.flush()
                os.fsync(f.fileno())
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        # 原子性地替换文件
        temp_file.rename(DATA_FILE)
        
    except Exception as e:
        st.error(f"保存数据时出错: {str(e)}")
        # 如果保存失败，尝试恢复备份
        if BACKUP_FILE.exists():
            shutil.copy2(BACKUP_FILE, DATA_FILE)
            st.warning("已从备份恢复数据")

def create_visualizations(health_data):
    if not health_data:
        return None
    
    # 转换为 DataFrame
    df = pd.DataFrame(health_data)
    df['date'] = pd.to_datetime(df['date'])
    
    # 按日期排序
    df = df.sort_values('date')
    
    # 创建图表
    charts = {}
    
    # 体重趋势图
    weight_fig = px.line(df, x='date', y='weight',
                        title='体重变化趋势',
                        labels={'weight': '体重 (kg)', 'date': '日期'})
    weight_fig.update_layout(
        xaxis_title='日期',
        yaxis_title='体重 (kg)',
        hovermode='x unified'
    )
    charts['weight'] = weight_fig
    
    # 步数柱状图
    steps_fig = px.bar(df, x='date', y='steps',
                      title='每日步数',
                      labels={'steps': '步数', 'date': '日期'})
    steps_fig.update_layout(
        xaxis_title='日期',
        yaxis_title='步数',
        hovermode='x unified'
    )
    charts['steps'] = steps_fig
    
    # 睡眠时间折线图
    sleep_fig = px.line(df, x='date', y='sleep_hours',
                       title='睡眠时间变化',
                       labels={'sleep_hours': '睡眠时间 (小时)', 'date': '日期'})
    sleep_fig.update_layout(
        xaxis_title='日期',
        yaxis_title='睡眠时间 (小时)',
        hovermode='x unified'
    )
    charts['sleep'] = sleep_fig
    
    return charts

def edit_record(record_index, health_data):
    record = health_data[record_index]
    st.write("编辑数据：")
    
    new_weight = st.number_input(
        "体重 (kg)", 
        min_value=0.0, 
        max_value=300.0, 
        value=float(record['weight']), 
        step=0.1,
        key=f"edit_weight_{record_index}"
    )
    
    new_steps = st.number_input(
        "步数", 
        min_value=0, 
        value=int(record['steps']), 
        step=100,
        key=f"edit_steps_{record_index}"
    )
    
    new_sleep = st.number_input(
        "睡眠时间 (小时)", 
        min_value=0.0, 
        max_value=24.0, 
        value=float(record['sleep_hours']), 
        step=0.5,
        key=f"edit_sleep_{record_index}"
    )
    
    if st.button("更新数据", key=f"update_{record_index}"):
        health_data[record_index].update({
            "weight": new_weight,
            "steps": new_steps,
            "sleep_hours": new_sleep
        })
        save_data(health_data)
        st.success("数据已更新！")
        st.rerun()

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
            # 检查是否已存在该日期的记录
            date_str = date.strftime("%Y-%m-%d")
            existing_record = next((i for i, record in enumerate(health_data) 
                                 if record['date'] == date_str), None)
            
            if existing_record is not None:
                st.warning("该日期已存在记录。是否要更新？")
                if st.button("确认更新", key="confirm_update"):
                    health_data[existing_record].update({
                        "weight": weight,
                        "steps": steps,
                        "sleep_hours": sleep_hours
                    })
                    save_data(health_data)
                    st.success("数据已更新！")
                    st.rerun()
            else:
                new_record = {
                    "date": date_str,
                    "weight": weight,
                    "steps": steps,
                    "sleep_hours": sleep_hours
                }
                health_data.append(new_record)
                save_data(health_data)
                st.success("数据已保存！")
                st.rerun()
    
    # 主页面 - 数据显示和可视化
    if health_data:
        # 创建可视化图表
        charts = create_visualizations(health_data)
        
        # 显示图表
        st.header("数据可视化")
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(charts['weight'], use_container_width=True)
            st.plotly_chart(charts['sleep'], use_container_width=True)
        
        with col2:
            st.plotly_chart(charts['steps'], use_container_width=True)
        
        # 显示历史记录（带编辑功能）
        st.header("历史记录")
        for i, record in enumerate(health_data):
            with st.expander(f"📅 {record['date']}"):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"体重: {record['weight']} kg")
                    st.write(f"步数: {record['steps']} 步")
                    st.write(f"睡眠时间: {record['sleep_hours']} 小时")
                with col2:
                    if st.button("编辑", key=f"edit_button_{i}"):
                        edit_record(i, health_data)
    else:
        st.info("还没有记录任何数据。请在左侧输入您的健康数据。")

if __name__ == "__main__":
    main()
