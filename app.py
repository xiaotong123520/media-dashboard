"""全网自媒体数据看板 · Streamlit 演示版
没有接入真实平台接口时，使用演示数据；接入后把 load_metrics 换成读数据库/调适配器即可。
"""
from datetime import date, timedelta

import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="自媒体数据看板", page_icon="📊", layout="wide")

PLATFORMS = {"douyin": "抖音", "bilibili": "B站", "kuaishou": "快手"}
METRICS = {"views": "播放量", "likes": "点赞", "comments": "评论", "followers": "粉丝数"}


@st.cache_data(ttl=3600)
def load_metrics(platform: str, days: int = 30) -> pd.DataFrame:
    """统一数据格式：date / platform / views / likes / comments / followers"""
    rng = np.random.default_rng({"douyin": 1, "bilibili": 2, "kuaishou": 3}[platform])
    base = {"douyin": 8000, "bilibili": 3000, "kuaishou": 5000}[platform]
    dates = [date.today() - timedelta(days=days - 1 - i) for i in range(days)]
    views = (base * (1 + 0.03 * np.arange(days)) * rng.uniform(0.7, 1.3, days)).astype(int)
    return pd.DataFrame({
        "date": pd.to_datetime(dates),
        "platform": platform,
        "views": views,
        "likes": (views * rng.uniform(0.04, 0.08, days)).astype(int),
        "comments": (views * rng.uniform(0.005, 0.015, days)).astype(int),
        "followers": (base // 2 + np.cumsum(rng.integers(5, 60, days))).astype(int),
    })


st.title("📊 自媒体数据看板")
st.caption("演示数据 · 接入开放平台授权后替换为真实数据")

platform = st.radio("平台", list(PLATFORMS), format_func=PLATFORMS.get, horizontal=True)
col_a, col_b = st.columns([1, 1])
metric = col_a.selectbox("指标", list(METRICS), format_func=METRICS.get)
days = col_b.select_slider("时间范围（天）", options=[7, 14, 30, 60, 90], value=30)

df = load_metrics(platform, days)
last, prev = df.iloc[-1], df.iloc[-2]

k1, k2, k3, k4 = st.columns(4)
for col, key in zip((k1, k2, k3, k4), METRICS):
    col.metric(METRICS[key], f"{int(last[key]):,}", f"{int(last[key] - prev[key]):+,}")

st.subheader(f"{PLATFORMS[platform]} · {METRICS[metric]}趋势")
st.line_chart(df.set_index("date")[[metric]].rename(columns={metric: METRICS[metric]}))

with st.expander("查看原始数据"):
    st.dataframe(df.rename(columns=METRICS), width="stretch", hide_index=True)
