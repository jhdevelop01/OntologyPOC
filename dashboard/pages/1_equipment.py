"""Equipment Overview Page"""

import streamlit as st
import pandas as pd
import plotly.express as px
from utils.neo4j_client import get_cached_client
from utils import queries

st.set_page_config(page_title="Equipment", page_icon="🏭", layout="wide")

st.title("🏭 장비 현황")
st.markdown("UPW 공정 장비 및 센서 현황")

try:
    client = get_cached_client()
except Exception as e:
    st.error(f"Neo4j 연결 실패: {e}")
    st.stop()

# Equipment list
st.header("장비 목록")
equipment = client.query(queries.GET_ALL_EQUIPMENT)

if equipment:
    df = pd.DataFrame(equipment)

    # Filter by type
    types = ['All'] + list(df['type'].unique())
    selected_type = st.selectbox("장비 타입 필터", types)

    if selected_type != 'All':
        df = df[df['type'] == selected_type]

    st.dataframe(df, use_container_width=True)

    # Stats chart
    st.header("장비 타입별 분포")
    stats = client.query(queries.GET_EQUIPMENT_STATS)
    if stats:
        df_stats = pd.DataFrame(stats)
        fig = px.pie(df_stats, values='count', names='type', title='장비 타입별 분포')
        st.plotly_chart(fig, use_container_width=True)
else:
    st.info("장비 데이터가 없습니다.")

# Equipment with sensors
st.header("장비별 센서 현황")
equipment_sensors = client.query(queries.GET_EQUIPMENT_WITH_SENSORS)

if equipment_sensors:
    for eq in equipment_sensors:
        with st.expander(f"🏭 {eq['equipmentName']} ({eq['equipmentId']})"):
            sensors = eq.get('sensors', [])
            if sensors:
                df_sensors = pd.DataFrame(sensors)
                st.dataframe(df_sensors, use_container_width=True)
            else:
                st.info("연결된 센서가 없습니다.")
else:
    st.info("센서 데이터가 없습니다.")
