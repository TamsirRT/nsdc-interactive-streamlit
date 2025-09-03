import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import time
from streamlit_autorefresh import st_autorefresh

gsheet_url = "https://docs.google.com/spreadsheets/d/1EBNzLbmHzFNX82xljJfAiPwb9yCH4E5Y7IZYSoSK6zc/edit?resourcekey=&gid=1110534495#gid=1110534495"
sheet_id = "1EBNzLbmHzFNX82xljJfAiPwb9yCH4E5Y7IZYSoSK6zc"
gsheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv"

st_autorefresh(interval = 10 * 1000, key="data_refresh")  # Refresh every 10 seconds
# # --- Load Data ---
# uploaded_file = st.file_uploader("📂 Upload form responses (CSV)", type="csv")

# if uploaded_file is None:
#     st.info("Please upload a CSV to continue.")
#     st.stop()
df = pd.read_csv(gsheet_url)
df

# --- Sticky Header & Filters ---
st.markdown("""
    <style>
    /* Sticky Title */
    .main-title {
        position: sticky;
        top: 0;
        z-index: 1000;
        background-color: white;
        padding: 15px 10px;
        border-bottom: 3px solid #FFD700;
    }

    /* Sticky Filters */
    div[data-testid="stHorizontalBlock"] {
        position: sticky;
        top: 70px; /* sits below title */
        z-index: 999;
        background-color: white;
        padding: 10px 5px;
        border-bottom: 2px solid #eee;
    }
    </style>
""", unsafe_allow_html=True)

# --- Dashboard Title ---
st.markdown('<div class="main-title">', unsafe_allow_html=True)
st.title("✨ NSDC Interest Dashboard")
st.caption("A live look at who’s joining, their vibes, and what excites them 🚀")
st.markdown('</div>', unsafe_allow_html=True)

# --- Filters ---
st.markdown("### 🔍 Quick Filters")
col1, col2 = st.columns([1, 1])
with col1:
    class_filter = st.multiselect(
        "Class Status", df["Class Status"].unique()
    )
with col2:
    exec_filter = st.multiselect(
        "Exec Role Interest",
        df["Would you like to be considered for an Executive Board role?"].unique()
    )


# Apply filters
filtered_df = df.copy()
if class_filter:
    filtered_df = filtered_df[filtered_df["Class Status"].isin(class_filter)]
if exec_filter:
    filtered_df = filtered_df[
        filtered_df["Would you like to be considered for an Executive Board role?"].isin(exec_filter)
    ]


# --- Helper function for light clean look ---
def clean_fig_layout(fig, title=None):
    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(color="#001F3F", size=14),
        title=dict(text=title, font=dict(size=18, color="#001F3F")),
        margin=dict(l=40, r=40, t=40, b=40),
    )
    return fig

# --- Vibe Check ---
st.markdown("## 😎 Vibe Check")
if "Choose the vibe that fits you best" in filtered_df.columns:
    vibe_fig = px.pie(
        filtered_df,
        names="Choose the vibe that fits you best",
        color_discrete_sequence=["#FFD700", "#001F3F", "#302D7B", "#AAAAAA"],
    )
    vibe_fig = clean_fig_layout(vibe_fig, "Choose the vibe that fits you best")
    st.plotly_chart(vibe_fig, use_container_width=True)

# --- Campus Culture ---
st.markdown("## 🏫 Favorite Campus Spots")
col1, col2 = st.columns(2)

with col1:
    study_counts = filtered_df["Choose your favorite study area on campus"].value_counts().head(5)
    study_fig = px.bar(
        study_counts,
        x=study_counts.values,
        y=study_counts.index,
        orientation="h",
        color=study_counts.values,
        color_continuous_scale="Blues",
    )
    study_fig = clean_fig_layout(study_fig, "Top Study Areas")
    st.plotly_chart(study_fig, use_container_width=True)

with col2:
    food_counts = filtered_df["Favorite Towson Hangout/Food Spots"].value_counts().head(5)
    food_fig = px.bar(
        food_counts,
        x=food_counts.values,
        y=food_counts.index,
        orientation="h",
        color=food_counts.values,
        color_continuous_scale="Oranges",
    )
    food_fig = clean_fig_layout(food_fig, "Top Food & Hangouts")
    st.plotly_chart(food_fig, use_container_width=True)

# --- Music & Entertainment ---
st.markdown("## 🎶 Music & Entertainment")
col3, col4 = st.columns(2)

with col3:
    songs = filtered_df["What's your favorite song (Ex. type N/A if None)"].dropna().head(10)
    st.subheader("🎵 Favorite Songs (Top 10)")
    st.dataframe(songs, use_container_width=True, height=250)

with col4:
    if "Favorite Movie/Show Genre?" in filtered_df.columns:
        genre_counts = filtered_df["Favorite Movie/Show Genre?"].value_counts().head(10)
        genre_fig = px.bar(
            genre_counts,
            x=genre_counts.values,
            y=genre_counts.index,
            orientation="h",
            color=genre_counts.values,
            color_continuous_scale="Viridis",
        )
        genre_fig = clean_fig_layout(genre_fig, "Favorite Movie/Show Genres")
        st.plotly_chart(genre_fig, use_container_width=True)

# --- Demographics: Class Status ---
st.markdown("## 🎓 Class Status Distribution")
class_fig = px.histogram(
    filtered_df,
    x="Class Status",
    color="Class Status",
    color_discrete_sequence=["#FFD700", "#001F3F", "#302D7B", "#FF5733", "#AAAAAA"],
)
class_fig = clean_fig_layout(class_fig, "Class Year Breakdown")
st.plotly_chart(class_fig, use_container_width=True)

# --- Skills Radar Chart ---
st.markdown("## 💡 Average Comfort Level by Skill")
skill_columns = [
    "Rate your comfort level with the following skills [Public speaking]",
    "Rate your comfort level with the following skills [Data analysis]",
    "Rate your comfort level with the following skills [Graphic design / social media]",
    "Rate your comfort level with the following skills [Event planning]",
    "Rate your comfort level with the following skills [Budgeting & finances]",
    "Rate your comfort level with the following skills [Coding/ Technical adept]",
]
skill_map = {"Not Comfortable": 1, "Some Comfort": 2, "Ok": 3, "Comfortable": 4, "Very Comfortable": 5}
df_numeric = filtered_df[skill_columns].replace(skill_map)
skill_means = df_numeric[skill_columns].mean()

radar_fig = go.Figure()
radar_fig.add_trace(
    go.Scatterpolar(
        r=skill_means.values,
        theta=[col.split("[")[-1][:-1] for col in skill_columns],
        fill="toself",
        name="Average Comfort",
        line_color="#001F3F",
        fillcolor="rgba(0,31,63,0.2)",
    )
)
radar_fig.update_layout(
    polar=dict(radialaxis=dict(visible=True, range=[0, 5], gridcolor="lightgray")),
    paper_bgcolor="white",
    font=dict(color="#001F3F"),
    showlegend=False,
    margin=dict(l=40, r=40, t=40, b=40),
)
st.plotly_chart(radar_fig, use_container_width=True)

# --- Interest Meeting Attendance ---
st.markdown("## 📅 Interest Meeting Plans")
attend_fig = px.pie(
    filtered_df,
    names="Do you plan to come to our Interest Meeting",
    color_discrete_sequence=["#FFD700", "#001F3F", "#AAAAAA"],
)
attend_fig = clean_fig_layout(attend_fig, "Interest Meeting Attendance")
st.plotly_chart(attend_fig, use_container_width=True)

# --- What Excites Students Most ---
st.markdown("## ✨ What Excites You About Joining?")
excites_text = " ".join(
    filtered_df["What excites you most about joining a student organization?"].dropna()
)
if excites_text:
    wordcloud = WordCloud(width=800, height=400, background_color="white", colormap="cividis").generate(excites_text)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig)
else:
    st.info("No responses yet for excitement question.")

# --- Event Interests ---
st.markdown("## 🎟️ Event Interests")
event_counts = (
    filtered_df["What type of events would you be most excited to plan or participate in?"]
    .value_counts()
    .head(10)
)
event_fig = px.bar(
    event_counts,
    x=event_counts.values,
    y=event_counts.index,
    orientation="h",
    color=event_counts.values,
    color_continuous_scale="sunset",
)
event_fig = clean_fig_layout(event_fig, "Top Event Preferences")
st.plotly_chart(event_fig, use_container_width=True)

# --- Individual Responses ---
st.markdown("## 📋 Explore Individual Responses")
st.dataframe(filtered_df, use_container_width=True, height=400)
