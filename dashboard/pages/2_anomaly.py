"""Anomaly Detection Page"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.neo4j_client import get_cached_client
from utils import queries

st.set_page_config(page_title="Anomaly Detection", page_icon="⚠️", layout="wide")

st.title("⚠️ 이상탐지 모니터링")
st.markdown("센서 데이터 기반 이상탐지 현황")

try:
    client = get_cached_client()
except Exception as e:
    st.error(f"Neo4j 연결 실패: {e}")
    st.stop()

# Anomaly summary
st.header("이상탐지 요약")

anomaly_counts = client.query(queries.GET_ANOMALY_COUNT_BY_THRESHOLD)
if anomaly_counts:
    col1, col2, col3 = st.columns(3)
    for i, item in enumerate(anomaly_counts):
        level = item.get('level', 'Unknown')
        count = item.get('count', 0)
        if 'Critical' in level:
            col1.metric("🔴 Critical", count)
        elif 'Warning' in level:
            col2.metric("🟡 Warning", count)
        else:
            col3.metric("🟢 Normal", count)

st.divider()

# Anomaly list
st.header("이상탐지 목록")

anomalies = client.query(queries.GET_ANOMALIES)
if anomalies:
    df = pd.DataFrame(anomalies)

    # Threshold filter
    threshold = st.slider("Anomaly Score 임계값", 0.0, 1.0, 0.5, 0.1)
    df_filtered = df[df['score'] >= threshold] if 'score' in df.columns else df

    # Display with color coding
    def color_score(val):
        if val is None:
            return ''
        if val >= 0.7:
            return 'background-color: #ff4444; color: white'
        elif val >= 0.5:
            return 'background-color: #ffaa00; color: black'
        return 'background-color: #44ff44; color: black'

    st.dataframe(
        df_filtered.style.map(color_score, subset=['score']),
        use_container_width=True
    )

    # Score distribution chart
    st.header("Score 분포")
    if 'score' in df.columns:
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df['sensorId'],
            y=df['score'],
            marker_color=['red' if s >= 0.7 else 'orange' if s >= 0.5 else 'green'
                         for s in df['score']]
        ))
        fig.add_hline(y=0.7, line_dash="dash", line_color="red", annotation_text="Critical (0.7)")
        fig.add_hline(y=0.5, line_dash="dash", line_color="orange", annotation_text="Warning (0.5)")
        fig.update_layout(
            title="센서별 Anomaly Score",
            xaxis_title="Sensor ID",
            yaxis_title="Anomaly Score"
        )
        st.plotly_chart(fig, use_container_width=True)
else:
    st.info("이상탐지 데이터가 없습니다.")
