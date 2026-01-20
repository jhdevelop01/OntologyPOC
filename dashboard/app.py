"""UPW Process Ontology Dashboard - Main App"""

import streamlit as st
import pandas as pd
from utils.neo4j_client import get_cached_client
from utils import queries

# Page config
st.set_page_config(
    page_title="UPW Process Dashboard",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title
st.title("💧 UPW Process Ontology Dashboard")
st.markdown("Ultra Pure Water 공정 모니터링 및 예측 정비 대시보드")

# Sidebar
st.sidebar.title("Navigation")
st.sidebar.markdown("페이지를 선택하세요")

# Connection status
try:
    client = get_cached_client()
    summary = client.query_single(queries.GET_DASHBOARD_SUMMARY)
    st.sidebar.success("✅ Neo4j Connected")
except Exception as e:
    st.sidebar.error(f"❌ Neo4j Connection Failed")
    st.error(f"Neo4j 연결 실패: {e}")
    st.info("Neo4j 서버가 실행 중인지 확인하세요: `docker compose up -d`")
    st.stop()

# Main dashboard - KPI Cards
st.header("📊 Overview")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        label="🏭 장비",
        value=summary.get('equipmentCount', 0)
    )

with col2:
    st.metric(
        label="📡 센서",
        value=summary.get('sensorCount', 0)
    )

with col3:
    st.metric(
        label="⚠️ 이상탐지",
        value=summary.get('anomalyCount', 0)
    )

with col4:
    st.metric(
        label="🔮 고장예측",
        value=summary.get('predictionCount', 0)
    )

with col5:
    st.metric(
        label="🔧 정비일정",
        value=summary.get('maintenanceCount', 0)
    )

st.divider()

# Quick view sections
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("⚠️ 최근 이상탐지")
    anomalies = client.query(queries.GET_ANOMALIES)
    if anomalies:
        df_anomalies = pd.DataFrame(anomalies)
        # Highlight high scores
        def highlight_score(val):
            if val is None:
                return ''
            if val >= 0.7:
                return 'background-color: #ff4444; color: white'
            elif val >= 0.5:
                return 'background-color: #ffaa00; color: black'
            return ''

        display_df = df_anomalies[['score', 'sensorId', 'description']].head(5)
        st.dataframe(
            display_df.style.map(highlight_score, subset=['score']),
            use_container_width=True
        )
    else:
        st.info("이상탐지 데이터가 없습니다.")

with col_right:
    st.subheader("🔮 고장 예측")
    predictions = client.query(queries.GET_FAILURE_PREDICTIONS)
    if predictions:
        df_predictions = pd.DataFrame(predictions)
        st.dataframe(
            df_predictions[['equipmentName', 'failureMode', 'predictedDate', 'confidence']].head(5),
            use_container_width=True
        )
    else:
        st.info("고장 예측 데이터가 없습니다.")

st.divider()

# Equipment overview
st.subheader("🏭 장비 현황")
equipment = client.query(queries.GET_ALL_EQUIPMENT)
if equipment:
    df_equipment = pd.DataFrame(equipment)
    st.dataframe(df_equipment, use_container_width=True)
else:
    st.info("장비 데이터가 없습니다.")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: gray;'>
    UPW Process Ontology Dashboard | Neo4j + Streamlit<br>
    📖 <a href='https://github.com/jhdevelop01/OntologyPOC'>GitHub Repository</a>
</div>
""", unsafe_allow_html=True)
