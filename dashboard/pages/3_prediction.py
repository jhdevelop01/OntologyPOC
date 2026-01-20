"""Failure Prediction Page"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from utils.neo4j_client import get_cached_client
from utils import queries

st.set_page_config(page_title="Failure Prediction", page_icon="🔮", layout="wide")

st.title("🔮 고장 예측")
st.markdown("장비 고장 예측 및 잔여 수명(RUL) 현황")

try:
    client = get_cached_client()
except Exception as e:
    st.error(f"Neo4j 연결 실패: {e}")
    st.stop()

# Predictions
predictions = client.query(queries.GET_FAILURE_PREDICTIONS)

if predictions:
    df = pd.DataFrame(predictions)

    # Summary cards
    st.header("예측 요약")
    col1, col2 = st.columns(2)

    with col1:
        st.metric("총 예측 건수", len(df))

    with col2:
        high_conf = len(df[df['confidence'] >= 0.7]) if 'confidence' in df.columns else 0
        st.metric("높은 신뢰도 (≥70%)", high_conf)

    st.divider()

    # Prediction details
    st.header("고장 예측 상세")

    for _, pred in df.iterrows():
        confidence = pred.get('confidence', 0) or 0
        rul = pred.get('rul', 0) or 0

        # Color based on urgency
        if confidence >= 0.7:
            status = "🔴"
        elif confidence >= 0.5:
            status = "🟡"
        else:
            status = "🟢"

        with st.expander(f"{status} {pred.get('equipmentName', 'Unknown')} - {pred.get('failureMode', 'Unknown')}"):
            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown("**예측 일자**")
                st.write(pred.get('predictedDate', 'N/A'))

            with col2:
                st.markdown("**신뢰도**")
                st.progress(confidence)
                st.write(f"{confidence*100:.1f}%")

            with col3:
                st.markdown("**잔여 수명 (RUL)**")
                st.write(f"{rul:.0f} 시간")

            if pred.get('comment'):
                st.markdown("**권장 조치**")
                st.info(pred.get('comment'))

    # Timeline visualization
    st.header("고장 예측 타임라인")

    if 'predictedDate' in df.columns:
        df_timeline = df.copy()
        df_timeline['predictedDate'] = pd.to_datetime(df_timeline['predictedDate'], errors='coerce')
        df_timeline = df_timeline.dropna(subset=['predictedDate'])

        if not df_timeline.empty:
            fig = px.timeline(
                df_timeline,
                x_start='predictedDate',
                x_end='predictedDate',
                y='equipmentName',
                color='failureMode',
                title='예측 고장 일정'
            )
            fig.update_layout(xaxis_title="Date", yaxis_title="Equipment")
            st.plotly_chart(fig, use_container_width=True)

    # RUL gauge chart
    st.header("잔여 수명 (RUL) 현황")

    fig = go.Figure()
    for _, pred in df.iterrows():
        rul = pred.get('rul', 0) or 0
        fig.add_trace(go.Bar(
            name=pred.get('equipmentName', 'Unknown'),
            x=[pred.get('equipmentName', 'Unknown')],
            y=[rul],
            text=[f"{rul:.0f}h"],
            textposition='auto'
        ))

    fig.update_layout(
        title="장비별 잔여 수명",
        xaxis_title="Equipment",
        yaxis_title="Remaining Useful Life (hours)",
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("고장 예측 데이터가 없습니다.")
