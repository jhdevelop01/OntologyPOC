"""Maintenance Schedule Page"""

import streamlit as st
import pandas as pd
import plotly.express as px
from utils.neo4j_client import get_cached_client
from utils import queries

st.set_page_config(page_title="Maintenance", page_icon="🔧", layout="wide")

st.title("🔧 정비 일정")
st.markdown("예방/예측/교정 정비 일정 관리")

try:
    client = get_cached_client()
except Exception as e:
    st.error(f"Neo4j 연결 실패: {e}")
    st.stop()

# Maintenance type summary
st.header("정비 유형별 현황")

type_counts = client.query(queries.GET_MAINTENANCE_BY_TYPE)
if type_counts:
    df_types = pd.DataFrame(type_counts)

    col1, col2 = st.columns([1, 2])

    with col1:
        for _, row in df_types.iterrows():
            mtype = row.get('type', 'Unknown')
            count = row.get('count', 0)
            if 'Preventive' in str(mtype):
                st.metric("🛡️ 예방 정비", count)
            elif 'Predictive' in str(mtype):
                st.metric("🔮 예측 정비", count)
            elif 'Corrective' in str(mtype):
                st.metric("🔧 교정 정비", count)

    with col2:
        fig = px.pie(df_types, values='count', names='type', title='정비 유형별 분포')
        st.plotly_chart(fig, use_container_width=True)

st.divider()

# Maintenance events
st.header("정비 일정 목록")

events = client.query(queries.GET_MAINTENANCE_EVENTS)
if events:
    df = pd.DataFrame(events)

    # Filters
    col1, col2, col3 = st.columns(3)

    with col1:
        status_filter = st.multiselect(
            "상태",
            options=['Scheduled', 'Completed'],
            default=['Scheduled']
        )

    with col2:
        if 'maintenanceType' in df.columns:
            types = df['maintenanceType'].dropna().unique().tolist()
            type_filter = st.multiselect("정비 유형", options=types, default=types)
        else:
            type_filter = []

    with col3:
        if 'priority' in df.columns:
            priorities = sorted(df['priority'].dropna().unique().tolist())
            priority_filter = st.multiselect(
                "우선순위",
                options=priorities,
                default=priorities,
                format_func=lambda x: f"P{int(x)}" if x else "N/A"
            )
        else:
            priority_filter = []

    # Apply filters
    df_filtered = df.copy()
    if status_filter and 'status' in df_filtered.columns:
        df_filtered = df_filtered[df_filtered['status'].isin(status_filter)]
    if type_filter and 'maintenanceType' in df_filtered.columns:
        df_filtered = df_filtered[df_filtered['maintenanceType'].isin(type_filter)]
    if priority_filter and 'priority' in df_filtered.columns:
        df_filtered = df_filtered[df_filtered['priority'].isin(priority_filter)]

    # Priority color coding
    def priority_color(val):
        if val == 1:
            return 'background-color: #ff4444; color: white'
        elif val == 2:
            return 'background-color: #ffaa00; color: black'
        elif val == 3:
            return 'background-color: #44ff44; color: black'
        return ''

    # Display
    display_cols = ['equipmentName', 'eventName', 'scheduledDate', 'priority', 'status', 'maintenanceType', 'duration']
    available_cols = [c for c in display_cols if c in df_filtered.columns]

    if not df_filtered.empty:
        styled_df = df_filtered[available_cols].style
        if 'priority' in available_cols:
            styled_df = styled_df.map(priority_color, subset=['priority'])

        st.dataframe(styled_df, use_container_width=True)
    else:
        st.info("필터 조건에 맞는 정비 일정이 없습니다.")

    # Timeline
    st.header("정비 타임라인")

    if 'scheduledDate' in df.columns:
        df_timeline = df.copy()
        df_timeline['scheduledDate'] = pd.to_datetime(df_timeline['scheduledDate'], errors='coerce')
        df_timeline = df_timeline.dropna(subset=['scheduledDate'])

        if not df_timeline.empty:
            fig = px.scatter(
                df_timeline,
                x='scheduledDate',
                y='equipmentName',
                color='maintenanceType' if 'maintenanceType' in df_timeline.columns else None,
                size='priority' if 'priority' in df_timeline.columns else None,
                hover_data=['eventName', 'status'],
                title='정비 일정 타임라인'
            )
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Equipment"
            )
            st.plotly_chart(fig, use_container_width=True)

    # Details
    st.header("정비 상세")

    for _, event in df.iterrows():
        priority = event.get('priority', 0)
        if priority == 1:
            icon = "🔴"
        elif priority == 2:
            icon = "🟡"
        else:
            icon = "🟢"

        status = event.get('status', 'Unknown')
        status_icon = "✅" if status == 'Completed' else "📅"

        with st.expander(f"{icon} {status_icon} {event.get('equipmentName', 'Unknown')} - {event.get('eventName', 'Unknown')}"):
            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"**정비 유형:** {event.get('maintenanceType', 'N/A')}")
                st.markdown(f"**예정일:** {event.get('scheduledDate', 'N/A')}")
                st.markdown(f"**상태:** {status}")

            with col2:
                st.markdown(f"**우선순위:** P{int(priority) if priority else 'N/A'}")
                st.markdown(f"**예상 소요시간:** {event.get('duration', 'N/A')} 시간")

            if event.get('description'):
                st.markdown(f"**설명:** {event.get('description')}")

else:
    st.info("정비 일정 데이터가 없습니다.")
