import streamlit as st

def main():
    st.title("健康数据追踪")
    st.write("欢迎使用健康数据追踪应用！")
    
    # 简单的输入框
    name = st.text_input("请输入您的名字")
    if name:
        st.write(f"你好，{name}！")
    
    # 简单的按钮
    if st.button("点击测试"):
        st.success("按钮工作正常！")

if __name__ == "__main__":
    main() 