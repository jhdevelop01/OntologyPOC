"""Energy Prediction Page"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.neo4j_client import get_cached_client
from utils import queries

st.set_page_config(page_title="Energy Forecast", page_icon="⚡", layout="wide")

st.title("⚡ 에너지 예측")
st.markdown("96포인트 (15분 간격) 일일 에너지 소비 예측")

try:
    client = get_cached_client()
except Exception as e:
    st.error(f"Neo4j 연결 실패: {e}")
    st.stop()

# Energy summary
st.header("에너지 예측 요약")

summary = client.query(queries.GET_ENERGY_SUMMARY)
if summary:
    s = summary[0]
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("📅 예측 일자", s.get('forecastDate', 'N/A'))

    with col2:
        total = s.get('totalEnergy', 0) or 0
        st.metric("📊 총 에너지", f"{total:.1f} kWh")

    with col3:
        peak = s.get('peakPower', 0) or 0
        st.metric("📈 피크 전력", f"{peak:.1f} kW")

    with col4:
        conf = s.get('confidence', 0) or 0
        st.metric("🎯 신뢰도", f"{conf*100:.0f}%")

st.divider()

# 96-point forecast chart
st.header("96포인트 에너지 예측")

forecast = client.query(queries.GET_ENERGY_FORECAST)
if forecast:
    df = pd.DataFrame(forecast)

    # Line chart
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['intervalIndex'],
        y=df['powerKW'],
        mode='lines+markers',
        name='Power (kW)',
        line=dict(color='#1f77b4', width=2),
        marker=dict(size=4)
    ))

    # Highlight peak periods (intervals 32-72, roughly 8am-6pm)
    peak_df = df[(df['intervalIndex'] >= 32) & (df['intervalIndex'] <= 72)]
    if not peak_df.empty:
        fig.add_vrect(
            x0=32, x1=72,
            fillcolor="rgba(255, 165, 0, 0.2)",
            layer="below",
            line_width=0,
            annotation_text="Peak Hours",
            annotation_position="top left"
        )

    fig.update_layout(
        title="15분 간격 전력 소비 예측",
        xaxis_title="Interval Index (0-95)",
        yaxis_title="Power (kW)",
        hovermode='x unified'
    )

    # Add time labels
    time_labels = {0: "00:00", 24: "06:00", 48: "12:00", 72: "18:00", 95: "23:45"}
    fig.update_xaxes(
        tickvals=list(time_labels.keys()),
        ticktext=list(time_labels.values())
    )

    st.plotly_chart(fig, use_container_width=True)

    # Statistics
    st.header("통계")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("평균 전력", f"{df['powerKW'].mean():.1f} kW")

    with col2:
        st.metric("최대 전력", f"{df['powerKW'].max():.1f} kW")

    with col3:
        st.metric("최소 전력", f"{df['powerKW'].min():.1f} kW")

    with col4:
        st.metric("표준편차", f"{df['powerKW'].std():.1f} kW")

    # Period analysis
    st.header("시간대별 분석")

    # Group by period
    def get_period(idx):
        if idx < 24:
            return "야간 (00:00-06:00)"
        elif idx < 48:
            return "오전 (06:00-12:00)"
        elif idx < 72:
            return "오후 (12:00-18:00)"
        else:
            return "저녁 (18:00-24:00)"

    df['period'] = df['intervalIndex'].apply(get_period)
    period_stats = df.groupby('period')['powerKW'].agg(['mean', 'max', 'min']).reset_index()
    period_stats.columns = ['시간대', '평균 (kW)', '최대 (kW)', '최소 (kW)']

    st.dataframe(period_stats, use_container_width=True)

    # Bar chart by period
    fig_bar = px.bar(
        period_stats,
        x='시간대',
        y='평균 (kW)',
        title='시간대별 평균 전력',
        color='평균 (kW)',
        color_continuous_scale='Blues'
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # Raw data
    with st.expander("📋 Raw Data"):
        st.dataframe(df, use_container_width=True)

else:
    st.info("에너지 예측 데이터가 없습니다.")
