import streamlit as st
import requests
import time

# 比特币数据API地址
COINGECKO_API_URL = 'https://api.coingecko.com/api/v3/simple/price'

# 价格显示模块
def get_bitcoin_price():
    try:
        params = {
            'ids': 'bitcoin',
            'vs_currencies': 'usd'
        }
        response = requests.get(COINGECKO_API_URL, params=params)
        response.raise_for_status()  # 检查请求是否成功
        data = response.json()
        return data['bitcoin']['usd']
    except requests.RequestException as e:
        st.error(f"无法获取比特币价格: {e}")
        return None

# 趋势显示模块
def get_bitcoin_price_change():
    try:
        params = {
            'ids': 'bitcoin',
            'vs_currencies': 'usd',
            'days': 1
        }
        response = requests.get(COINGECKO_API_URL, params=params)
        response.raise_for_status()  # 检查请求是否成功
        data = response.json()
        price = data['bitcoin']['usd']
        # 假设昨天的价格为10000（这里只是示例，实际需要获取昨天价格）
        yesterday_price = 10000
        change_amount = price - yesterday_price
        change_percentage = (change_amount / yesterday_price) * 100
        return change_amount, change_percentage
    except requests.RequestException as e:
        st.error(f"无法获取比特币价格变化趋势: {e}")
        return None, None

# 错误处理与加载状态模块
def display_price():
    with st.spinner('正在加载比特币价格...'):
        price = get_bitcoin_price()
        if price is not None:
            st.write(f"比特币当前价格（USD）: {price}")
            change_amount, change_percentage = get_bitcoin_price_change()
            if change_amount is not None and change_percentage is not None:
                st.write(f"24小时价格变化额: {change_amount}")
                st.write(f"24小时价格变化百分比: {change_percentage:.2f}%")

# 刷新功能模块
def add_refresh_button():
    if st.button('刷新价格'):
        display_price()

# 主程序
def main():
    st.title('比特币价格显示应用')
    display_price()
    add_refresh_button()

if __name__ == '__main__':  
    main()