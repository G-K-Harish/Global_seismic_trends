import os

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine, text


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Global Seismic Trends",
    page_icon="🌍",
    layout="wide"
)


# ============================================================
# ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "earthquake_db")


# ============================================================
# DATABASE CONNECTION
# ============================================================

@st.cache_resource
def get_engine():
    return create_engine(
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )


engine = get_engine()


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    query = """
    SELECT
        id,
        time,
        updated,
        longitude,
        latitude,
        depth_km,
        mag,
        magType,
        place,
        status,
        tsunami,
        alert,
        felt,
        cdi,
        mmi,
        sig,
        net,
        nst,
        dmin,
        rms,
        gap,
        types,
        code,
        ids,
        sources,
        type,
        country,
        year,
        month,
        day,
        day_of_week,
        hour,
        depth_category,
        mag_category
    FROM earthquakes;
    """

    with engine.connect() as connection:
        data = pd.read_sql(text(query), connection)

    data["time"] = pd.to_datetime(data["time"])

    return data


df = load_data()


# ============================================================
# TITLE
# ============================================================

st.title("🌍 Global Seismic Trends")
st.subheader("Data-Driven Earthquake Insights")

st.markdown(
    """
    Explore global earthquake activity using the cleaned USGS earthquake
    dataset stored in MySQL.
    """
)


# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.header("Dashboard Filters")

min_year = int(df["year"].min())
max_year = int(df["year"].max())

year_range = st.sidebar.slider(
    "Year Range",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year)
)

event_types = sorted(df["type"].dropna().unique())

selected_types = st.sidebar.multiselect(
    "Event Type",
    event_types,
    default=["earthquake"] if "earthquake" in event_types else event_types[:1]
)

min_mag = float(df["mag"].min())
max_mag = float(df["mag"].max())

mag_range = st.sidebar.slider(
    "Magnitude Range",
    min_value=min_mag,
    max_value=max_mag,
    value=(min_mag, max_mag)
)

depth_categories = sorted(
    df["depth_category"].dropna().unique()
)

selected_depth = st.sidebar.multiselect(
    "Depth Category",
    depth_categories,
    default=depth_categories
)

alert_values = sorted(
    df["alert"].dropna().unique()
)

selected_alerts = st.sidebar.multiselect(
    "Alert Level",
    alert_values,
    default=alert_values
)


# ============================================================
# APPLY FILTERS
# ============================================================

filtered_df = df[
    (df["year"].between(year_range[0], year_range[1]))
    & (df["mag"].between(mag_range[0], mag_range[1]))
    & (df["type"].isin(selected_types))
    & (df["depth_category"].isin(selected_depth))
]

if selected_alerts:
    filtered_df = filtered_df[
        filtered_df["alert"].isna()
        | filtered_df["alert"].isin(selected_alerts)
    ]


# ============================================================
# KEY METRICS
# ============================================================

st.header("Key Metrics")

col1, col2, col3, col4, col5 = st.columns(5)

total_events = len(filtered_df)

earthquake_count = filtered_df["type"].eq("earthquake").sum()

average_magnitude = filtered_df["mag"].mean()

maximum_magnitude = filtered_df["mag"].max()

tsunami_count = filtered_df["tsunami"].eq(1).sum()

col1.metric(
    "Total Events",
    f"{total_events:,}"
)

col2.metric(
    "Earthquakes",
    f"{earthquake_count:,}"
)

col3.metric(
    "Average Magnitude",
    f"{average_magnitude:.2f}"
    if pd.notna(average_magnitude)
    else "N/A"
)

col4.metric(
    "Maximum Magnitude",
    f"{maximum_magnitude:.1f}"
    if pd.notna(maximum_magnitude)
    else "N/A"
)

col5.metric(
    "Tsunami Events",
    f"{tsunami_count:,}"
)

st.divider()


# ============================================================
# OVERVIEW
# ============================================================

st.header("Earthquake Overview")

col1, col2 = st.columns(2)


with col1:

    yearly_counts = (
        filtered_df[
            filtered_df["type"] == "earthquake"
        ]
        .groupby("year")
        .size()
        .reset_index(name="earthquake_count")
    )

    fig_year = px.line(
        yearly_counts,
        x="year",
        y="earthquake_count",
        markers=True,
        title="Earthquakes by Year"
    )

    fig_year.update_layout(
        xaxis_title="Year",
        yaxis_title="Number of Earthquakes"
    )

    st.plotly_chart(
        fig_year,
        width="stretch"
    )


with col2:

    monthly_counts = (
        filtered_df[
            filtered_df["type"] == "earthquake"
        ]
        .groupby("month")
        .size()
        .reset_index(name="earthquake_count")
    )

    fig_month = px.bar(
        monthly_counts,
        x="month",
        y="earthquake_count",
        title="Earthquakes by Month"
    )

    fig_month.update_layout(
        xaxis_title="Month",
        yaxis_title="Number of Earthquakes"
    )

    st.plotly_chart(
        fig_month,
        width="stretch"
    )


# ============================================================
# MAGNITUDE & DEPTH
# ============================================================

st.header("Magnitude & Depth Analysis")

col1, col2 = st.columns(2)


with col1:

    magnitude_data = filtered_df[
        filtered_df["mag"].notna()
    ]

    fig_mag = px.histogram(
        magnitude_data,
        x="mag",
        nbins=40,
        title="Magnitude Distribution"
    )

    fig_mag.update_layout(
        xaxis_title="Magnitude",
        yaxis_title="Number of Events"
    )

    st.plotly_chart(
        fig_mag,
        width="stretch"
    )


with col2:

    depth_data = (
        filtered_df["depth_category"]
        .value_counts()
        .reset_index()
    )

    depth_data.columns = [
        "depth_category",
        "count"
    ]

    fig_depth = px.pie(
        depth_data,
        names="depth_category",
        values="count",
        title="Shallow vs Deep Earthquakes"
    )

    st.plotly_chart(
        fig_depth,
        width="stretch"
    )


# ============================================================
# GLOBAL EARTHQUAKE MAP
# ============================================================

st.header("Global Earthquake Map")

map_df = filtered_df[
    filtered_df["latitude"].notna()
    & filtered_df["longitude"].notna()
].copy()

# Keep map responsive
if len(map_df) > 5000:
    map_df = map_df.nlargest(5000, "mag")


fig_map = px.scatter_geo(
    map_df,
    lat="latitude",
    lon="longitude",
    size="mag",
    color="mag",
    hover_name="place",
    hover_data=[
        "mag",
        "depth_km",
        "country",
        "time"
    ],
    title="Earthquake Locations"
)

fig_map.update_layout(
    geo=dict(
        showland=True,
        showcountries=True
    )
)

st.plotly_chart(
    fig_map,
    width="stretch"
)


# ============================================================
# ALERT & TSUNAMI
# ============================================================

st.header("Alerts & Tsunami Analysis")

col1, col2 = st.columns(2)


with col1:

    alert_data = (
        filtered_df[
            filtered_df["alert"].notna()
        ]
        .groupby("alert")
        .size()
        .reset_index(name="count")
    )

    fig_alert = px.bar(
        alert_data,
        x="alert",
        y="count",
        title="Earthquakes by Alert Level"
    )

    st.plotly_chart(
        fig_alert,
        width="stretch"
    )


with col2:

    tsunami_data = (
        filtered_df[
            filtered_df["tsunami"] == 1
        ]
        .groupby("year")
        .size()
        .reset_index(name="tsunami_count")
    )

    fig_tsunami = px.bar(
        tsunami_data,
        x="year",
        y="tsunami_count",
        title="Tsunami-Triggered Events by Year"
    )

    st.plotly_chart(
        fig_tsunami,
        width="stretch"
    )


# ============================================================
# EVENT TYPES
# ============================================================

st.header("Event Type Analysis")

event_data = (
    filtered_df["type"]
    .value_counts()
    .reset_index()
)

event_data.columns = [
    "event_type",
    "count"
]

fig_events = px.bar(
    event_data.head(15),
    x="count",
    y="event_type",
    orientation="h",
    title="Most Common Event Types"
)

st.plotly_chart(
    fig_events,
    width="stretch"
)


# ============================================================
# REPORTING NETWORK
# ============================================================

st.header("Reporting Network Analysis")

network_data = (
    filtered_df[
        filtered_df["type"] == "earthquake"
    ]["net"]
    .value_counts()
    .head(15)
    .reset_index()
)

network_data.columns = [
    "network",
    "earthquake_count"
]

fig_network = px.bar(
    network_data,
    x="network",
    y="earthquake_count",
    title="Top Reporting Networks"
)

st.plotly_chart(
    fig_network,
    width="stretch"
)


# ============================================================
# GEOGRAPHIC ANALYSIS
# ============================================================

st.header("Geographic Analysis")

country_data = (
    filtered_df[
        filtered_df["type"] == "earthquake"
    ]["country"]
    .value_counts()
    .head(15)
    .reset_index()
)

country_data.columns = [
    "country",
    "earthquake_count"
]

fig_country = px.bar(
    country_data,
    x="earthquake_count",
    y="country",
    orientation="h",
    title="Top Geographic Labels by Earthquake Frequency"
)

st.plotly_chart(
    fig_country,
    width="stretch"
)


# ============================================================
# TOP 10 STRONGEST EARTHQUAKES
# ============================================================

st.header("Top 10 Strongest Earthquakes")

top_10 = (
    filtered_df[
        filtered_df["mag"].notna()
    ]
    .nlargest(10, "mag")
    [
        [
            "id",
            "time",
            "mag",
            "depth_km",
            "place",
            "country",
            "alert"
        ]
    ]
)

st.dataframe(
    top_10,
    width="stretch",
    hide_index=True
)


# ============================================================
# TOP 10 DEEPEST EARTHQUAKES
# ============================================================

st.header("Top 10 Deepest Earthquakes")

deepest_10 = (
    filtered_df[
        filtered_df["depth_km"].notna()
    ]
    .nlargest(10, "depth_km")
    [
        [
            "id",
            "time",
            "depth_km",
            "mag",
            "place",
            "country"
        ]
    ]
)

st.dataframe(
    deepest_10,
    width="stretch",
    hide_index=True
)


# ============================================================
# HIGH STATION COVERAGE
# ============================================================

st.header("Station Coverage")

median_nst = filtered_df["nst"].median()

high_station_df = (
    filtered_df[
        filtered_df["nst"] > median_nst
    ]
    [
        [
            "id",
            "time",
            "place",
            "nst",
            "mag"
        ]
    ]
    .sort_values(
        "nst",
        ascending=False
    )
    .head(20)
)

st.write(
    f"Median station coverage (nst): **{median_nst:.0f} stations**"
)

st.dataframe(
    high_station_df,
    width="stretch",
    hide_index=True
)


# ============================================================
# DATA EXPLORER
# ============================================================

st.header("Data Explorer")

st.write(
    f"Showing {len(filtered_df):,} filtered records."
)

display_columns = [
    "id",
    "time",
    "mag",
    "depth_km",
    "place",
    "country",
    "type",
    "status",
    "tsunami",
    "alert",
    "nst",
    "rms",
    "gap"
]

st.dataframe(
    filtered_df[display_columns].head(500),
    width="stretch",
    hide_index=True
)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Global Seismic Trends | Data source: USGS Earthquake API | "
    "Analysis: Pandas, MySQL, SQLAlchemy and Streamlit"
)
