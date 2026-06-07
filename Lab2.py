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
    return df

df = load_data()

# ══════════════════════════════════════════════════════════════════════════════
# 1. EXPLORATORY GRAPHICS - Interactive Scatter Plot
# ══════════════════════════════════════════════════════════════════════════════
if page == "1. Exploratory Graphics":
    st.title("Exploratory Graphics vs Presentation Graphics")
    st.header("Exploratory Graphics: Interactive Scatter Plot")

    # Let user pick X and Y columns from numeric columns
    numeric_cols = df.select_dtypes(include='number').columns.tolist()

    col1, col2 = st.columns(2)
    with col1:
        x_axis = st.selectbox("Select X-axis indicator", numeric_cols, index=0)
    with col2:
        y_axis = st.selectbox("Select Y-axis indicator", numeric_cols, index=1)

    # Find region/country columns dynamically
    region_col = None
    country_col = None
    for col in df.columns:
        if 'region' in col.lower():
            region_col = col
        if 'country' in col.lower():
            country_col = col

    tooltip_cols = [c for c in [country_col, region_col, x_axis, y_axis] if c]

    scatter_chart = alt.Chart(df).mark_circle(size=60).encode(
        x=alt.X(f'{x_axis}:Q', title=x_axis),
        y=alt.Y(f'{y_axis}:Q', title=y_axis),
        color=alt.Color(f'{region_col}:N', title='Region') if region_col else alt.value('steelblue'),
        tooltip=tooltip_cols
    ).interactive().properties(
        height=450,
        title=f'{x_axis} vs {y_axis} by Country'
    )

    st.altair_chart(scatter_chart, use_container_width=True)
    st.write("""
    This scatter plot is an example of exploratory graphics. Each point represents a country, 
    coloured by region, allowing you to interactively explore relationships between two SDG 
    indicators. Hover over any data point to see the country name, region, and exact values. 
    Patterns such as clusters or outliers reveal how development indicators relate across regions.
    """)

# ══════════════════════════════════════════════════════════════════════════════
# 2. PRESENTATION GRAPHICS - Static Bar Chart
# ══════════════════════════════════════════════════════════════════════════════
elif page == "2. Presentation Graphics":
    st.title("Exploratory Graphics vs Presentation Graphics")
    st.header("Presentation Graphics: Static Bar Chart")

    # Find region and SDG score columns
    region_col = None
    score_col = None
    for col in df.columns:
        if 'region' in col.lower():
            region_col = col
        if 'sdg' in col.lower() and 'score' in col.lower() or 'index' in col.lower() and 'score' in col.lower():
            score_col = col

    if region_col and score_col:
        avg_score = df.groupby(region_col)[score_col].mean().reset_index()
        avg_score.columns = ['Region', 'Average SDG Score']
        avg_score = avg_score.sort_values('Average SDG Score', ascending=False)

        bar_chart = alt.Chart(avg_score).mark_bar().encode(
            x=alt.X('Average SDG Score:Q', title='Average SDG Index Score'),
            y=alt.Y('Region:N', sort='-x', title='Region'),
            color=alt.Color('Region:N', legend=None),
            tooltip=['Region', 'Average SDG Score']
        ).properties(
            height=400,
            title='Average SDG Score by Region'
        )

        st.altair_chart(bar_chart, use_container_width=True)
        st.write("""
        This static bar chart presents the average SDG Index Score grouped by world region. 
        It clearly shows which regions are performing best in sustainable development without 
        any interactivity. Europe and high-income regions tend to score highest, while 
        Sub-Saharan Africa and South Asia face the greatest development challenges, 
        highlighting significant global inequality in sustainable development progress.
        """)
    else:
        st.warning("Could not find region or SDG score columns. Please check your dataset column names.")
        st.write("Available columns:", df.columns.tolist())

# ══════════════════════════════════════════════════════════════════════════════
# 3. LINKED HIGHLIGHTING
# ══════════════════════════════════════════════════════════════════════════════
elif page == "3. Linked Highlighting":
    st.title("Interactive Linked Highlighting for High-Dimensional Data")

    region_col = None
    score_col = None
    numeric_cols = df.select_dtypes(include='number').columns.tolist()

    for col in df.columns:
        if 'region' in col.lower():
            region_col = col
        if 'sdg' in col.lower() and 'score' in col.lower() or 'index' in col.lower() and 'score' in col.lower():
            score_col = col

    if not score_col and numeric_cols:
        score_col = numeric_cols[0]

    x_col = numeric_cols[1] if len(numeric_cols) > 1 else numeric_cols[0]

    if region_col and score_col:
        # Shared selection
        highlight = alt.selection_point(fields=[region_col], on='mouseover')

        # Scatter plot
        scatter = alt.Chart(df).mark_circle(size=60).encode(
            x=alt.X(f'{x_col}:Q', title=x_col),
            y=alt.Y(f'{score_col}:Q', title='SDG Score'),
            color=alt.condition(highlight, f'{region_col}:N', alt.value('lightgray')),
            tooltip=[region_col, score_col, x_col]
        ).add_params(highlight).properties(
            height=350,
            title='SDG Score vs Indicator (hover to highlight)'
        )

        # Bar chart
        avg_score = df.groupby(region_col)[score_col].mean().reset_index()
        avg_score.columns = ['Region', 'Average SDG Score']

        bar = alt.Chart(avg_score).mark_bar().encode(
            x=alt.X('Average SDG Score:Q'),
            y=alt.Y('Region:N', sort='-x'),
            color=alt.condition(highlight, 'Region:N', alt.value('lightgray')),
            tooltip=['Region', 'Average SDG Score']
        ).add_params(highlight).properties(
            height=350,
            title='Average SDG Score by Region (hover to highlight)'
        )

        st.altair_chart(scatter & bar, use_container_width=True)
        st.write("""
        Hovering over a region in either chart highlights the corresponding data in the other chart. 
        This linking reveals patterns that individual charts cannot show alone — for example, 
        you can see which countries within a region are pulling the average score up or down. 
        Linked highlighting is a powerful technique for exploring high-dimensional data interactively.
        """)
    else:
        st.warning("Could not find required columns. Available columns: " + str(df.columns.tolist()))

# ══════════════════════════════════════════════════════════════════════════════
# 4. SDG REFLECTION
# ══════════════════════════════════════════════════════════════════════════════
elif page == "4. SDG Reflection":
    st.title("SDG Reflection: Progress Across Regions")
    st.header("Finding Appropriate Graphics and Linking Multivariate Context")

    region_col = None
    for col in df.columns:
        if 'region' in col.lower():
            region_col = col

    numeric_cols = df.select_dtypes(include='number').columns.tolist()

    # Let user pick an SDG goal column to explore
    selected_col = st.selectbox("Select an SDG indicator to explore", numeric_cols)

    if region_col:
        # Box/bar chart showing distribution of selected SDG by region
        region_avg = df.groupby(region_col)[selected_col].mean().reset_index()
        region_avg.columns = ['Region', 'Score']

        bar = alt.Chart(region_avg).mark_bar().encode(
            x=alt.X('Score:Q', title=f'Average {selected_col}'),
            y=alt.Y('Region:N', sort='-x', title='Region'),
            color=alt.Color('Region:N', legend=None),
            tooltip=['Region', 'Score']
        ).properties(
            height=400,
            title=f'Average {selected_col} by Region'
        ).interactive()

        st.altair_chart(bar, use_container_width=True)

        # Scatter showing spread within regions
        scatter = alt.Chart(df).mark_circle(size=50, opacity=0.6).encode(
            x=alt.X(f'{selected_col}:Q', title=selected_col),
            y=alt.Y(f'{region_col}:N', title='Region'),
            color=alt.Color(f'{region_col}:N', legend=None),
            tooltip=[region_col, selected_col]
        ).properties(
            height=400,
            title=f'Distribution of {selected_col} within Regions'
        ).interactive()

        st.altair_chart(scatter, use_container_width=True)

    st.subheader("SDG Reflection")
    st.write(f"""
    The visualizations above explore **{selected_col}** across world regions, revealing 
    significant disparities in sustainable development progress. The bar chart shows regional 
    averages, while the scatter plot below reveals the spread of individual country scores 
    within each region — highlighting that even within regions, there is considerable variation 
    in development outcomes.

    The UN Sustainable Development Goals represent a global commitment to ending poverty, 
    protecting the planet, and ensuring prosperity for all by 2030. The SDG Index Score 
    measures how well each country is progressing toward all 17 goals. Data clearly shows 
    that wealthier regions such as Europe and North America consistently outperform lower-income 
    regions, particularly Sub-Saharan Africa and South Asia. This inequality underscores the 
    urgent need for international cooperation, targeted investment, and policy reform to support 
    developing nations in meeting these critical global targets. Without addressing these gaps, 
    achieving the 2030 Agenda will remain an aspirational goal rather than a measurable reality 
    for billions of people worldwide.
    """)
