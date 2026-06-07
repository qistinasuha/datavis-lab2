import streamlit as st
import pandas as pd
import altair as alt

# ── Sidebar Navigation ─────────────────────────────────────────────────────────
st.sidebar.title("Lab 2 - Altair Visualizations")
st.sidebar.markdown("Use the menu below to explore each section.")
page = st.sidebar.selectbox(
    "Choose a section",
    [
        "1. Exploratory Graphics",
        "2. Presentation Graphics",
        "3. Linked Highlighting",
        "4. SDG Reflection"
    ]
)

# ── Load Data ──────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv('sdg.csv', encoding='latin1')
    df.columns = df.columns.str.strip()
    # Fix BOM character in first column if present
    df.rename(columns={df.columns[0]: 'country_code'}, inplace=True)
    return df

df = load_data()

# Use latest year only for cleaner charts
latest_year = df['year'].max()
df_latest = df[df['year'] == latest_year].copy()

# ══════════════════════════════════════════════════════════════════════════════
# 1. EXPLORATORY GRAPHICS - Interactive Scatter Plot
# ══════════════════════════════════════════════════════════════════════════════
if page == "1. Exploratory Graphics":
    st.title("Exploratory Graphics vs Presentation Graphics")
    st.header("Exploratory Graphics: Interactive Scatter Plot")

    goal_cols = [c for c in df.columns if c.startswith('goal_')]

    col1, col2 = st.columns(2)
    with col1:
        x_axis = st.selectbox("Select X-axis indicator", goal_cols, index=0)
    with col2:
        y_axis = st.selectbox("Select Y-axis indicator", goal_cols, index=1)

    scatter_chart = alt.Chart(df_latest).mark_circle(size=60).encode(
        x=alt.X(f'{x_axis}:Q', title=x_axis),
        y=alt.Y(f'{y_axis}:Q', title=y_axis),
        color=alt.Color('sdg_index_score:Q', scale=alt.Scale(scheme='viridis'), title='SDG Index Score'),
        tooltip=['country', 'sdg_index_score', x_axis, y_axis]
    ).interactive().properties(
        height=450,
        title=f'{x_axis} vs {y_axis} by Country ({latest_year})'
    )

    st.altair_chart(scatter_chart, use_container_width=True)
    st.write(f"""
    This scatter plot is an example of exploratory graphics using {latest_year} SDG data.
    Each point represents a country, coloured by its overall SDG Index Score.
    Hover over any data point to see the country name and exact indicator values.
    Patterns such as clusters or outliers reveal how individual SDG goals relate
    to each other and to overall development performance across countries.
    """)

# ══════════════════════════════════════════════════════════════════════════════
# 2. PRESENTATION GRAPHICS - Static Bar Chart
# ══════════════════════════════════════════════════════════════════════════════
elif page == "2. Presentation Graphics":
    st.title("Exploratory Graphics vs Presentation Graphics")
    st.header("Presentation Graphics: Static Bar Chart")

    # Top 20 countries by SDG index score
    top20 = df_latest.nlargest(20, 'sdg_index_score')[['country', 'sdg_index_score']].reset_index(drop=True)

    bar_chart = alt.Chart(top20).mark_bar().encode(
        x=alt.X('sdg_index_score:Q', title='SDG Index Score'),
        y=alt.Y('country:N', sort='-x', title='Country'),
        color=alt.Color('sdg_index_score:Q', scale=alt.Scale(scheme='greens'), legend=None),
        tooltip=['country', 'sdg_index_score']
    ).properties(
        height=500,
        title=f'Top 20 Countries by SDG Index Score ({latest_year})'
    )

    st.altair_chart(bar_chart, use_container_width=True)
    st.write(f"""
    This static bar chart presents the top 20 countries ranked by their SDG Index Score in {latest_year}.
    It clearly communicates which nations are performing best in sustainable development without
    any interactivity. Nordic countries such as Finland, Sweden, and Denmark consistently top
    the rankings, reflecting their strong commitment to social welfare, clean energy, and
    inclusive governance — key pillars of the UN Sustainable Development Goals.
    """)

# ══════════════════════════════════════════════════════════════════════════════
# 3. LINKED HIGHLIGHTING
# ══════════════════════════════════════════════════════════════════════════════
elif page == "3. Linked Highlighting":
    st.title("Interactive Linked Highlighting for High-Dimensional Data")

    goal_cols = [c for c in df.columns if c.startswith('goal_')]
    selected_goal = st.selectbox("Select a goal to compare with SDG Index Score", goal_cols, index=3)

    # Shared selection based on country
    highlight = alt.selection_point(fields=['country'], on='mouseover')

    # Scatter plot
    scatter = alt.Chart(df_latest).mark_circle(size=60).encode(
        x=alt.X(f'{selected_goal}:Q', title=selected_goal),
        y=alt.Y('sdg_index_score:Q', title='SDG Index Score'),
        color=alt.condition(highlight, alt.value('#E8593C'), alt.value('lightgray')),
        tooltip=['country', 'sdg_index_score', selected_goal]
    ).add_params(highlight).properties(
        height=350,
        title=f'{selected_goal} vs SDG Index Score'
    )

    # Bar chart - top 15 countries
    top15 = df_latest.nlargest(15, 'sdg_index_score')[['country', 'sdg_index_score']]
    bar = alt.Chart(top15).mark_bar().encode(
        x=alt.X('sdg_index_score:Q', title='SDG Index Score'),
        y=alt.Y('country:N', sort='-x', title='Country'),
        color=alt.condition(highlight, alt.value('#1D9E75'), alt.value('lightgray')),
        tooltip=['country', 'sdg_index_score']
    ).add_params(highlight).properties(
        height=350,
        title='Top 15 Countries by SDG Score (hover to highlight)'
    )

    st.altair_chart(scatter & bar, use_container_width=True)
    st.write("""
    Hovering over a country in either chart highlights the corresponding data point in the other.
    This linking reveals patterns that individual charts cannot show alone — for example,
    you can immediately see where a top-ranked country sits on the scatter plot relative to
    its individual goal score. Linked highlighting is a powerful technique for exploring
    high-dimensional SDG data interactively across multiple views simultaneously.
    """)

# ══════════════════════════════════════════════════════════════════════════════
# 4. SDG REFLECTION
# ══════════════════════════════════════════════════════════════════════════════
elif page == "4. SDG Reflection":
    st.title("SDG Reflection: Progress Over Time")
    st.header("Finding Appropriate Graphics and Linking Multivariate Context")

    goal_cols = [c for c in df.columns if c.startswith('goal_')]
    selected_goal = st.selectbox("Select an SDG goal to explore over time", goal_cols, index=3)

    # Top 5 countries for selected goal in latest year
    top5_countries = df_latest.nlargest(5, selected_goal)['country'].tolist()
    df_top5 = df[df['country'].isin(top5_countries)][['country', 'year', selected_goal]].dropna()

    # Line chart showing progress over time
    line = alt.Chart(df_top5).mark_line(point=True).encode(
        x=alt.X('year:O', title='Year'),
        y=alt.Y(f'{selected_goal}:Q', title=f'{selected_goal} Score'),
        color=alt.Color('country:N', title='Country'),
        tooltip=['country', 'year', selected_goal]
    ).properties(
        height=400,
        title=f'Progress of {selected_goal} Over Time (Top 5 Countries)'
    ).interactive()

    st.altair_chart(line, use_container_width=True)

    # Bar chart for all countries in latest year
    bar = alt.Chart(df_latest.dropna(subset=[selected_goal]).nlargest(20, selected_goal)).mark_bar().encode(
        x=alt.X(f'{selected_goal}:Q', title=f'{selected_goal} Score'),
        y=alt.Y('country:N', sort='-x', title='Country'),
        color=alt.Color(f'{selected_goal}:Q', scale=alt.Scale(scheme='blues'), legend=None),
        tooltip=['country', selected_goal]
    ).properties(
        height=450,
        title=f'Top 20 Countries for {selected_goal} ({latest_year})'
    )

    st.altair_chart(bar, use_container_width=True)

    