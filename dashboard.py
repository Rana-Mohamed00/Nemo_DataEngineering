import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from Database.database import get_connection

colors = {
    "orange": "#F97316",
    "orangelight" : "#FFF7ED",
    "red": "#DC2626",
    "lightred": "#FEF2F2",
    "darkred": "#9A3412",
    "purple": "#7C3AED",
    "lightpurple":"#F5F3FF",
    "darkpurple": "#4F46E5",
    "pink": "#DB2777",
    "lightBlue": "#0891B2",
    "green": "#16A34A",
    "darkGreen": "#0F766E",
    "lightgreen" :"#ECFDF5",
    "lightBlack": "#475569"
}

st.set_page_config(
    page_title="F1 Telemetry Dashboard",
    page_icon="🏎️",
    layout="wide"
)

st.markdown(
    '<style>div.block-container{padding-top:1rem;}</style>',
    unsafe_allow_html=True
)

st.title("🏎️ F1 Telemetry Dashboard")

connection = get_connection()
clean_data = pd.read_sql(
    "SELECT * FROM cleansed_telemetry",
    connection
)
dlq_data = pd.read_sql(
    "SELECT * FROM dead_letter",
    connection
)
connection.close()

total = len(clean_data) + len(dlq_data)
clean_rate =int( (len(clean_data) / total * 100))
print("Sucess read")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(
        f"""
        <div style="
            background-color: {colors['orangelight']};
            padding:20px;
            border-radius:15px;
            border-left:5px solid {colors['orange']};
            text-align:center;
        ">
            <h4 style="color:{colors['darkred']};">Total Records</h4>
            <h1 style="color:{colors['orange']};">{total}</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f"""
        <div style="
            background-color:{colors['lightgreen']};
            padding:20px;
            border-radius:15px;
            border-left:5px solid {colors['green']};
            text-align:center;
        ">
            <h4 style="color:{colors['darkGreen']};">Clean Records</h4>
            <h1 style="color:{colors['green']};">{len(clean_data)}</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        f"""
        <div style="
            background-color:{colors['lightred']};
            padding:20px;
            border-radius:15px;
            border-left:5px solid {colors['red']};
            text-align:center;
        ">
            <h4 style="color: {colors['darkred']};">DLQ Records</h4>
            <h1 style="color:{colors['red']};">{len(dlq_data)}</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

with col4:
    st.markdown(
        f"""
        <div style="
            background-color:{colors['lightpurple']};
            padding:20px;
            border-radius:15px;
            border-left:5px solid {colors['purple']};
            text-align:center;
        ">
            <h4 style="color: {colors['darkpurple']};">Clean Rate</h4>
            <h1 style="color: {colors['purple']};">{clean_rate}%</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

col1, col2, col3 = st.columns(3)
with col1:

    pie_data = {
        "Status": ["Clean", "DLQ"],
        "Count": [
            len(clean_data),
            len(dlq_data)
        ]
    }

    fig = px.pie(
        pie_data,
        names="Status",
        values="Count",
        title="Data Quality Distribution",
        color="Status",
        color_discrete_map={
            "Clean": colors["green"],
            "DLQ": colors["red"]
        }
    )
    fig.update_xaxes(rangemode="nonnegative")
    st.plotly_chart(fig)

with col2:

    chart_quality = pd.DataFrame({
        "Status": ["Clean", "DLQ"],
        "Records": [
            len(clean_data),
            len(dlq_data)
        ]
    })

    fig = px.bar(
        chart_quality,
        x="Status",
        y="Records",
        title="Data Quality Records",
        color="Status",
        color_discrete_map={
            "Clean": colors['darkGreen'],
            "DLQ": colors["pink"]
        }
    )
    fig.update_xaxes(rangemode="nonnegative")
    st.plotly_chart(fig )

with col3:

    clean_rate = len(clean_data) / total * 100

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=clean_rate,
            title={"text": "Clean Rate"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": colors["green"]},
                "steps": [
                    {
                        "range": [0, 50],
                        "color": colors['lightred']
                    },
                    {
                        "range": [50, 80],
                        "color": colors['orangelight']
                    },
                    {
                        "range": [80, 100],
                        "color": colors["lightgreen"]
                    }
                ]
            }
        )
    )
    fig.update_xaxes(rangemode="nonnegative")
    st.plotly_chart(fig)

st.subheader("🏎️ Telemetry Analysis")

col1, col2, col3, col4 = st.columns(4)
with col1:

    fig = px.histogram(
        clean_data,
        x="speed",
        title="Speed Distribution",
        color_discrete_sequence=[
            colors["orange"]
        ]
    )
    fig.update_xaxes(rangemode="nonnegative")
    st.plotly_chart(fig )

with col2:

    fig = px.scatter(
        clean_data,
        x="rpm",
        y="speed",
        title="RPM vs Speed",
        color_discrete_sequence=[
            colors["purple"]
        ]
    )
    fig.update_xaxes(rangemode="nonnegative")
    st.plotly_chart(fig)

with col3:
    fig = px.histogram(
        clean_data,
        x="drs",
        title="DRS Distribution",
        color_discrete_sequence=[
            colors["lightBlue"]
        ]
    )
    fig.update_xaxes(rangemode="nonnegative")
    st.plotly_chart(fig)

with col4:

    fig = px.scatter(
        clean_data,
        x="throttle",
        y="speed",
        title="Throttle vs Speed",
        color_discrete_sequence=[
            colors["pink"]
        ]
    )

    st.plotly_chart(fig)

col1, col2, col3, col4 = st.columns(4)
with col1:

    gear_speed = (
        clean_data
        .groupby("ngear")["speed"]
        .mean()
        .reset_index()
    )

    fig = px.bar(
        gear_speed,
        x="ngear",
        y="speed",
        title="Average Speed by Gear",
        color="ngear",
       
    )

    st.plotly_chart(fig)

with col2:

    gear_count = clean_data["ngear"].value_counts()

    gear_labels = [
        f"Gear {gear}"
        for gear in gear_count.index
    ]

    fig = px.pie(
        values=gear_count.values,
        names=gear_labels,
        title="Gear Distribution",
        color_discrete_sequence=[
            colors['purple'],
            colors['lightBlue'],
            colors['orange'],
            colors['red'],
            colors['green'],
            colors['pink']
        ]
    )

    st.plotly_chart(fig )

with col3:

    drs_speed = (
        clean_data
        .groupby("drs")["speed"]
        .mean()
        .reset_index()
    )

    fig = px.bar(
        drs_speed,
        x="drs",
        y="speed",
        title="Average Speed with DRS",
        color="drs",
        color_discrete_sequence=[
            colors["orange"],
            colors["darkGreen"]
        ]
    )

    st.plotly_chart(fig)

with col4:

    fig = px.scatter(
        clean_data,
        x="brake",
        y="speed",
        title="Brake vs Speed",
        color_discrete_sequence=[
            colors["red"]
        ]
    )

    st.plotly_chart(fig)

col1, col2, col3 = st.columns(3)
with col1:

    fig = px.box(
        clean_data,
        y="speed",
        title="Speed Distribution & Outliers",
        color_discrete_sequence=[
            colors["purple"]
        ]
    )

    st.plotly_chart(fig)

with col2:

    fig = px.line(
        clean_data,
        y="speed",
        title="Speed Over Telemetry Readings",
        color_discrete_sequence=[
            colors["green"]
        ]
    )

    st.plotly_chart(fig)
with col3:

    gear_rpm = (
        clean_data
        .groupby("ngear")["rpm"]
        .mean()
        .reset_index()
    )

    fig = px.bar(
        gear_rpm,
        x="ngear",
        y="rpm",
        title="Average RPM by Gear",
        color="ngear"
    )
    st.plotly_chart(fig)