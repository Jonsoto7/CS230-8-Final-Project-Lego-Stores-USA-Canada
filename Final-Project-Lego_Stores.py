"""

Jonathan Soto
CS230-8

Final Project - Lego Stores




"""


import os
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pydeck as pdk

script_dir = os.path.dirname(os.path.abspath(__file__))
data_file = os.path.join(script_dir, "lego_stores.csv")

st.set_page_config(
    page_title="Lego Stores",
    layout="wide",
    initial_sidebar_state="expanded",
)

unsafe_allow_html = True

@st.cache_data
def load_data(filepath = None):

    if filepath is None:
        filepath = data_file


    try:
        df = pd.read_csv(filepath)

        df["latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
        df["lonitude"] = pd.to_numeric(df["Longitude"], errors="coerce")
        df = df.dropna(subset=["Latitude", "Longitude"])
        df["State"] = df["State"].astype(str).str.strip()
        df["City"] = df["City"].astype(str).str.strip()
        df["Country"] = df["Country"].astype(str).str.strip()
        df["Store Name"] = df["Store Name"].astype(str).str.strip()
        return df
    except FileNotFoundError:
        st.error("File not found.")

        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error: {e}")
        return pd.DataFrame()

def det_summary_stats(df):

    total = len(df)
    country_counts = df["Country"].value_counts().to_dict()
    top_states = df["State"].value_counts().idxmax() if not df.empty else None
    return total, country_counts, top_states

df_all = load_data()
df_check = load_data(filepath = data_file)

if df_all.empty:
    st.error("No data found.")
    st.stop()

st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/2/24/LEGO_logo.svg",
                 width= 100,
                 )

st.sidebar.tile("filter stores")

country_options = ["All"] + sorted(df_all["Country"].unique().tolist())
selected_country = st.sidebar.selectbox("Select Country", country_options)
if selected_country == "All":
    state_pool = df_all
else:
    state_pool = df_all[df_all["Country"] == selected_country]

state_options = sorted(state_pool["State"].unique().tolist())

selected_states = st.sidebar.multislect(
    "selected state",
    options=state_options,
    default=[],
    help = "leave blank"
)
min_stores = st.sidebar.slider(
    "min stores per state (bar chart)",
    min_value = 1, max_value = 10, value = 2, step = 1,
)

st.sidebar.markdown("--")
st.sidebar.markdown("Lego Stores USA & Canada")

df_filtered = df_all[df_all["Country"] == selected_country] if selected_country != "all" else df_all.copy()

if selected_states:
    df_filtered = df_filtered[df_filtered["State"].isin(selected_states)]

    st.title("Lego Stores USA & Canada")
    st.markdown(
"Explore how LEGO Retail stores are spread out across North America "
    )

total, country_counts,top_state = get_summary_stats(df_filtered)
usa_count= country_counts.get("USA", 0)
canada_count= country_counts.get("Canada", 0)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="Total Stores", value=total)
with col2:
    st.metric(label="USA Stores", value= usa_count)
with col3:
    st.metric(label="Canada Stores", value=canada_count)
with col4:
    st.metric(label="Top State / Province", value=top_state)

st.markdown("---")

st.subheader("# Stores per State / Province")
st.markdown("Showing State / Provinces with atleast {min_stores} stores. Adjust the slider in sllidebar.")

state_counts = df_filtered["State"].value_coiunts().reset_index()
state_counts.columns = ["State","Count"]
state_counts_filtered = state_counts[state_counts["Count"] >= min_stores].sort_values("Count", ascending = False)

if not state_counts_filtered.empty:
    fig1, ax1 = plt.subplots(figsize=(10,5))


    us_states = df_all[df_all["State"] == "USA"]["State"].unique().tolist()
    colors = ["red" if s in us_states else "blue" for s in state_counts_filtered["State"]]

    bars = ax1.bar(
        state_counts_filtered["State"], state_counts_filtered["Count"],
        colors = colors, edgecolor = "white", linewidth = 0.5,
    )

    ax1.set_title("Number of USA & Canada Stores by State and Province", fontsize = 20, fontweight = "bold", color = "black")
    ax1.set_xlabel("State / Province", fontsize = 10,)
    ax1.set_ylabel("Number of USA & Canada Stores", fontsize = 10,)
    ax1.tick_params(axis="x", rotation=60, labelsize = 8)
    ax1.yaxis.set_major_locator(plt.MaxNLocator(Integer=True))
    ax1.grid(axis="y", alpha=0.5, linestyle="--")
    ax1.set_facecolor("grey")
    fig1.patch.set_facecolor("white")

    red_patch = mpatches.Patch(color="red", label="USA")
    blue_patch = mpatches.Patch(color="blue", label="Canada")
    ax1.legend(handles=[red_patch, blue_patch], fontsize=10, loc="upper right")

    for bar in bars:
        h = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width() / 2, h + 0.05,
             str(int(h)), ha="center", va="bottom", fontsize= 8, color = "black")

    st.pyplot(fig1)
else:
    st.error("No data found.")

st.markdown("---")

st.subheader("USA v Canada distribution")

col_pie, col_table = st.columns([1,1])

with col_pie:
    country_summary = df_filtered["Country"].value_counts()
    if len(country_summary) > 0:
        fig2, ax2 = plt.subplots(figsize=(5,5))
        wedge_colors = ["red", "blue", "yellow"]
        wedges, texts, autotexts = ax2.pie(
            country_summary.values,
            lables=["USA" if c == "USA" else "Canada" for c in country_summary.index],
            autopct="%1.1f%%",
            colors = wedge_colors[:len(country_summary)],
            startangle = 140,
            wedgeprops = dict(edgecolor="white", linewidth=2),
            textprops = {"fontsize": 10},
        )

        for ar in autotexts:
            at.set_color("white")
            at.set_fontweight("bold")
        ax2.set_title( "Stores by Country", fontsize = 12, fontweight = "bold")
        st.pyplot(fig2)

with col_table:
        st.markdown("Filtered Store list")
        display_cols = ["Store Name", "City", "State", "Country"]
        st.dataframe(df_filtered[display_cols].reset_index(drop = True), height = 300, use_container_width = True)

st.markdown("---")

st.subheader("Top States by Store Count")

top_n = st.slider("Show Top States", min_value=3, max_value = 15, value = 10, step = 1)

top_states = df_all["State"].value_counts().head(top_n).reset_index()
top_states.columns = ["State", "Count"]

top_states["In Filter"] = top_states["State"].apply(
    lambda s: "✓" if (not selected_states or s in selected_states) else "-"
)
st.dataframe(top_states, use_container_width = True, hide_index = True)

st.markdown("---")

st.subheader("Top States by Country and Province")
st.write("Store counts per state / province by country.")

pivot_df = df_all.pivot_table(
    index = "State",
    columns = "Country",
    values = "Store Name",
    aggfunc = "count", fill_value = 0,
)
pivot_df["Total"] = pivot_df.sum(axis=1)
pivot_df = pivot_df.sort_values("Total", ascending=False)
st.dataframe(pivot_df, use_container_width = True)

st.markdown("---")

def build_map_data(df):
    rows = []
    for _, row in df.iterrows():
        label = f"{row['Store Name']} {row['City']}, {row['State']}"
        rows.append({
            "lat": row["Latitude"],
            "lon": row["Longitude"],
            "tooltip": label,
            "country": row["Country"],
            "name": row["Store Name"],
        })

    map_df = pd.DataFrame(rows)
    legoland_names = [r["name"] for r in rows if "LEGOLAND" in r["name"].upper()]

    country_dict = {}
    for r in rows:
        c = r["country"]
        country_dict[c] = country_dict.get(c, 0) + 1

    return map_df, country_dict, legoland_names
    
st.subheader("Interactive Lego Store Map")
st.write("Red = USA | Blue = Canada" )

map_data, country_dict, legoland_names = build_map_data(df_filtered)

if not map_data.empty:
    map_data["color"] = map_data["country"].apply(
        lambda c: [208,16,18,200] if c == "USA" else [0,51,153,200]
    )

    view_state = pdk.ViewState(
        Latitude = map_data["lat"].mean(),
        Longitude = map_data["lon"].mean(),
        zoom = 3,
        pitch = 30,
    )

    scatter_layer = pdk.Layer(
        "Scatter",
        data = [map_data],
        get_position = ["lon", "lat"],
        get_fill_color = ["colo"],
        get_radius = 35000,
        pickable = True,
        auto_highlight = True,
        highlight_color = [255,215,0,255],
    )

    tooltip = {"html": "<b>{tooltip}</b>"}

    deck = pdk.Deck(
        layers = [scatter_layer],
        initial_view_state = view_state,
        tooltip= tooltip,
        map_style="mapbox://styles/mapbox/light-v9",
    )
    st.pydeck_chart(deck)

    if legoland_names:
        st.write("Lego Land locations in current filter", ','.join(legoland_names))
    else:
        st.write("No Lego Land locations in current filter")

    st.markdown("---")

    st.caption("CS230-8 Final Project | Data: Lego Stores USA & Canada | Made with Streamlit, Pandas & Motlib") 









