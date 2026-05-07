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

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(SCRIPT_DIR, "lego_stores.csv")

st.set_page_config(
    page_title="Lego Stores",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data
def load_data(filepath=None):
    if filepath is None:
        filepath = DATA_FILE
    try:
        df = pd.read_csv(filepath)
        df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")   
        df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce") 
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



def get_summary_stats(df):   
    total = len(df)
    country_counts = df["Country"].value_counts().to_dict()
    top_state = df["State"].value_counts().idxmax() if not df.empty else "N/A"
    return total, country_counts, top_state


df_all = load_data()
df_check = load_data(filepath=DATA_FILE)

if df_all.empty:
    st.error("No data found.")
    st.stop()


st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/2/24/LEGO_logo.svg", width=100)
st.sidebar.title("Filter Stores")


country_options = ["All"] + sorted(df_all["Country"].unique().tolist())
selected_country = st.sidebar.selectbox("Select Country", country_options)

if selected_country == "All":
    state_pool = df_all
else:
    state_pool = df_all[df_all["Country"] == selected_country]

state_options = sorted(state_pool["State"].unique().tolist())


selected_states = st.sidebar.multiselect(
    "Select State(s) / Province(s)",
    options=state_options,
    default=[],
    help="Leave blank to show all states.",
)


min_stores = st.sidebar.slider(
    "Min Stores per State (bar chart)",
    min_value=1, max_value=10, value=2, step=1,
)

st.sidebar.markdown("---")
st.sidebar.markdown("LEGO Stores USA & Canada")


if selected_country != "All":
    df_filtered = df_all[df_all["Country"] == selected_country]
else:
    df_filtered = df_all.copy()


if selected_states:
    df_filtered = df_filtered[df_filtered["State"].isin(selected_states)]


st.title("LEGO Stores USA & Canada")
st.markdown("Explore how LEGO retail stores are spread out across North America.")


total, country_counts, top_state = get_summary_stats(df_filtered)
usa_count = country_counts.get("USA", 0)
canada_count = country_counts.get("CAN", 0)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="Total Stores", value=total)
with col2:
    st.metric(label="USA Stores", value=usa_count)
with col3:
    st.metric(label="Canada Stores", value=canada_count)
with col4:
    st.metric(label="Top State / Province", value=top_state)

st.divider()


st.subheader("Stores per State / Province")
st.markdown(f"Showing states/provinces with at least {min_stores} store(s). Adjust the slider in the sidebar.")


state_counts = df_filtered["State"].value_counts().reset_index()
state_counts.columns = ["State", "Count"]
state_counts_filtered = state_counts[state_counts["Count"] >= min_stores].sort_values("Count", ascending=False)

if not state_counts_filtered.empty:
    fig1, ax1 = plt.subplots(figsize=(10, 5))


    us_states = df_all[df_all["Country"] == "USA"]["State"].unique().tolist()  
    colors = ["red" if s in us_states else "blue" for s in state_counts_filtered["State"]]

    bars = ax1.bar(
        state_counts_filtered["State"], state_counts_filtered["Count"],
        color=colors, edgecolor="white", linewidth=0.5,  
    )

    ax1.set_title("Number of LEGO Stores by State / Province", fontsize=15, fontweight="bold", color="black")
    ax1.set_xlabel("State / Province", fontsize=10)
    ax1.set_ylabel("Number of Stores", fontsize=10)
    ax1.tick_params(axis="x", rotation=60, labelsize=8)
    ax1.yaxis.set_major_locator(plt.MaxNLocator(integer=True))  
    ax1.grid(axis="y", alpha=0.5, linestyle="--")
    ax1.set_facecolor("lightgrey")
    fig1.patch.set_facecolor("white")

    red_patch = mpatches.Patch(color="red", label="USA")
    blue_patch = mpatches.Patch(color="blue", label="Canada")
    ax1.legend(handles=[red_patch, blue_patch], fontsize=10, loc="upper right")

   
    for bar in bars:
        h = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width() / 2, h + 0.05,
                 str(int(h)), ha="center", va="bottom", fontsize=8, color="black")

    st.pyplot(fig1)
else:
    st.info("No states meet the current filter. Try lowering the slider.")

st.divider()


st.subheader("USA vs Canada Distribution")

col_pie, col_table = st.columns([1, 1])

with col_pie:
    country_summary = df_filtered["Country"].value_counts()
    if len(country_summary) > 0:
        fig2, ax2 = plt.subplots(figsize=(5, 5))
        wedge_colors = ["red", "blue", "yellow"]
        wedges, texts, autotexts = ax2.pie(
            country_summary.values,
            labels=["USA" if c == "USA" else "Canada" for c in country_summary.index],  
            autopct="%1.1f%%",
            colors=wedge_colors[:len(country_summary)],
            startangle=140,
            wedgeprops=dict(edgecolor="white", linewidth=2),
            textprops={"fontsize": 10},
        )
        for at in autotexts: 
            at.set_color("white")
            at.set_fontweight("bold")
        ax2.set_title("Stores by Country", fontsize=12, fontweight="bold")
        st.pyplot(fig2)

with col_table:
    st.markdown("**Filtered Store List**")
    display_cols = ["Store Name", "City", "State", "Country"]
    st.dataframe(df_filtered[display_cols].reset_index(drop=True), height=300, use_container_width=True)

st.divider()

st.subheader("Top States by Store Count")

top_n = st.slider("Show Top N States", min_value=3, max_value=15, value=10, step=1)

top_states = df_all["State"].value_counts().head(top_n).reset_index()
top_states.columns = ["State", "Store Count"]


top_states["In Filter"] = top_states["State"].apply(
    lambda s: "✓" if (not selected_states or s in selected_states) else "-"
)
st.dataframe(top_states, use_container_width=True, hide_index=True)

st.divider()

st.subheader("Stores by State & Country")
st.write("Store counts per state / province by country.")

pivot_df = df_all.pivot_table(
    index="State", columns="Country", values="Store Name",
    aggfunc="count", fill_value=0,
)
pivot_df["Total"] = pivot_df.sum(axis=1)
pivot_df = pivot_df.sort_values("Total", ascending=False)
st.dataframe(pivot_df, use_container_width=True)

st.divider()


def build_map_data(df):
    rows = []
    for _, row in df.iterrows():
        label = f"{row['Store Name']} — {row['City']}, {row['State']}"
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


st.subheader("Interactive LEGO Store Map")
st.write("Red = USA | Blue = Canada. Hover over a dot to see the store name.")

map_data, country_dict, legoland_names = build_map_data(df_filtered)

if not map_data.empty:
    map_data["color"] = map_data["country"].apply(
        lambda c: [208, 16, 18, 200] if c == "USA" else [0, 51, 153, 200]
    )

    view_state = pdk.ViewState(
        latitude=map_data["lat"].mean(),   
        longitude=map_data["lon"].mean(),  
        zoom=3,
        pitch=30,
    )

    scatter_layer = pdk.Layer(
        "ScatterplotLayer",          
        data=map_data,              
        get_position=["lon", "lat"],
        get_fill_color="color",     
        get_radius=35000,
        pickable=True,
        auto_highlight=True,
        highlight_color=[255, 215, 0, 255],
    )

    tooltip = {"html": "<b>{tooltip}</b>"}

    deck = pdk.Deck(
        layers=[scatter_layer],
        initial_view_state=view_state,
        tooltip=tooltip,
        map_style="mapbox://styles/mapbox/light-v9",
    )
    st.pydeck_chart(deck)

    if legoland_names:
        st.write("🎢 LEGOLAND locations in current filter:", ", ".join(legoland_names))
    else:
        st.write("No LEGOLAND locations in current filter.")

else:
    st.info("No stores match the current filters. Try broadening your selection.")

st.divider()
st.caption("CS230-8 Final Project | Data: LEGO Stores USA & Canada | Made with Streamlit, Pandas & Matplotlib")
