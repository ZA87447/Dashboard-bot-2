import streamlit as st
import pandas as pd
import plotly.express as px

# Page Config
st.set_page_config(page_title="Tire Market Dashboard", layout="wide")

# Initialize session state for view preference if not already set
if 'view_mode' not in st.session_state:
    # Default to auto-detection
    st.session_state.view_mode = 'auto'

# Add view mode toggle in sidebar
st.sidebar.title("📱 View Settings")
view_mode = st.sidebar.radio(
    "Select View Mode:",
    options=["Auto-detect", "Desktop View", "Mobile View"],
    index=0,
    help="Choose how you want to view the dashboard"
)

# Set the view mode based on selection
if view_mode == "Desktop View":
    st.session_state.view_mode = 'desktop'
elif view_mode == "Mobile View":
    st.session_state.view_mode = 'mobile'
else:
    st.session_state.view_mode = 'auto'

# Add CSS for responsive design based on view mode
if st.session_state.view_mode == 'mobile':
    # Force mobile view
    st.markdown("""
    <style>
        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
        h1 {
            font-size: 1.5rem !important;
        }
        h2 {
            font-size: 1.3rem !important;
        }
        h3, h4, h5 {
            font-size: 1.1rem !important;
        }
        .stMetric {
            padding: 10px 5px !important;
        }
        .card {
            padding: 10px !important;
        }
        /* Force columns to stack */
        [data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
            min-width: 100% !important;
        }
    </style>
    """, unsafe_allow_html=True)
    is_mobile_view = True
elif st.session_state.view_mode == 'desktop':
    # Force desktop view
    is_mobile_view = False
else:
    # Auto-detect - add responsive CSS that only applies on small screens
    st.markdown("""
    <style>
        @media (max-width: 768px) {
            .main .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }
            h1 {
                font-size: 1.5rem !important;
            }
            h2 {
                font-size: 1.3rem !important;
            }
            h3, h4, h5 {
                font-size: 1.1rem !important;
            }
            .stMetric {
                padding: 10px 5px !important;
            }
            .card {
                padding: 10px !important;
            }
        }
    </style>
    """, unsafe_allow_html=True)
    # Auto-detect for columns
    is_mobile_view = st.session_state.get('detected_mobile', False)

# Add common styles
st.markdown("""
<style>
    .card {
        background-color: #F8F9FA;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
        text-align: center;
        margin-bottom: 20px;
    }
    .icon {
        font-size: 30px;
        color: #6C63FF;
    }
    .title {
        font-weight: bold;
        font-size: 20px;
        margin-bottom: 10px;
    }
    .data-row {
        display: flex;
        justify-content: space-between;
        padding: 10px 20px;
        border-top: 1px solid #E0E0E0;
        font-size: 16px;
    }
    .data-row:first-child {
        border-top: none;
    }
    .highlight {
        color: #6C63FF;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Add device detection JavaScript
st.components.v1.html("""
<script>
    // Detect if the device is mobile
    const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent) || window.innerWidth < 768;
    
    // Store this information to be used by Streamlit
    if (window.parent.streamlit) {
        const data = {
            detected_mobile: isMobile
        };
        window.parent.streamlit.setComponentValue(data);
    }
</script>
""", height=0)

# Load dataset
df = pd.read_csv("Data/202425_data_2countries_3tiresizes (1).csv")

# Sidebar Filters with Icons
st.sidebar.header("🔍 Filters")
selected_year = st.sidebar.selectbox("📅 Select Year", df["SALES_YEAR"].unique())
selected_countries = st.sidebar.selectbox("🌍 Select Countries", df["COUNTRY_OR_TERRITORY"].unique())
selected_tire_size = st.sidebar.selectbox("📏 Select Tire Size", df["TIRE_SIZE"].unique())

# Filtered Data
df_filtered = df[
    (df["SALES_YEAR"] == selected_year) &
    (df["COUNTRY_OR_TERRITORY"] == (selected_countries)) & 
    (df["TIRE_SIZE"] == selected_tire_size)
]

# ---- Main Layout ----
st.title("🚗 Tire Market Dashboard")
st.markdown("##### 📊 Market insights and competitor analysis")

# Conditional layout based on view mode
if is_mobile_view:
    # MOBILE LAYOUT - STACKED SINGLE COLUMN
    
    # ---- Industry & Goodyear Sales ----
    st.subheader("📊 Industry & Goodyear Sales")
    sales_data = df_filtered[["TOTAL_INDUSTRY_SALES", "GOODYEAR_SALES"]].drop_duplicates().melt(var_name="Sales Type", value_name="Sales Value")
    
    # Rename for display only
    sales_type_mapping = {
        "TOTAL_INDUSTRY_SALES": "Total Industry Sales",
        "GOODYEAR_SALES": "Goodyear Sales"
    }
    sales_data["Sales Type"] = sales_data["Sales Type"].map(sales_type_mapping)

    
    fig_sales = px.bar(
        sales_data,
        x="Sales Type",
        y="Sales Value",
        title="Industry & Goodyear Sales",
        text_auto=True,
        color="Sales Type",
        color_discrete_map={
            "Total Industry Sales": "#1f77b4",  # Blue
            "Goodyear Sales": "#ffcc00"  # Yellow
        }
    )
    fig_sales.update_layout(
        xaxis_title="Sales Type",
        yaxis_title="Sales Value"
    )
    st.plotly_chart(fig_sales, use_container_width=True)
    
    # ---- Market Share ----
    st.subheader("📊 Market Share of Goodyear")
    market_share = df_filtered[["SOM_OF_BRAND"]].drop_duplicates()["SOM_OF_BRAND"].mean()
    st.markdown("Market Share (%)", help="Calculated based on SOM of the selected brand.")
    st.markdown(f"<h3>{market_share * 100:.2f}%</h3>", unsafe_allow_html=True)
    
    # ---- Competitor Sales ----
    st.subheader("🏆 Competitor Sales Comparison")
    df_competitor_sales = (
        df_filtered[["COMPETITOR_BRAND", "COMPETITOR_BRAND_SALES"]]
        .drop_duplicates()
        .groupby("COMPETITOR_BRAND", as_index=False)
        .sum()
        .sort_values(by="COMPETITOR_BRAND_SALES", ascending=False)
        .head(10)  # Limit to top 10 competitors
    )
    fig_comp = px.bar(
        df_competitor_sales, 
        x="COMPETITOR_BRAND", 
        y="COMPETITOR_BRAND_SALES", 
        title="Top Competitor Sales", 
        text_auto=True,
        color_discrete_sequence=["#00CC96"]
    )
    fig_comp.update_layout(
        xaxis_title="Competitor brand",
        yaxis_title="Competitor brand sales",
        xaxis={'categoryorder': 'total descending'}
    )
    st.plotly_chart(fig_comp, use_container_width=True)

    
    # ---- Market Share Distribution ----
    st.subheader("📊 Market Share Distribution")
    df_valid_brands = df_filtered.dropna(subset=["BRAND_NAME"])
    brand_counts = df_valid_brands["BRAND_NAME"].value_counts().reset_index()
    brand_counts.columns = ["BRAND_NAME", "COUNT"]
    total_brands = brand_counts["COUNT"].sum()
    brand_counts["PERCENTAGE"] = (brand_counts["COUNT"] / total_brands) * 100
    fig_pie = px.pie(
        brand_counts, 
        names="BRAND_NAME", 
        values="PERCENTAGE", 
        title="Market Share Distribution",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_pie.update_traces(
        textinfo="label",
        hovertemplate="<b>%{label}</b><br>Market Share: %{value:.2f}%"
    )
    st.plotly_chart(fig_pie, use_container_width=True)
    
    # ---- Top 10 Competitors Table ----
    st.subheader("🥇 Top 10 Competitors")

    # Rename columns
    df_top_competitors = df_filtered.rename(columns={
        "COMPETITOR_BRAND": "Competitor Brand",
        "COMPETITOR_BRAND_SALES": "Competitor Sales",
        "COMPETITOR_SOM_OF_BRAND": "Competitor Market Share"
    })


    # Drop duplicates before aggregation
    df_top_competitors = df_top_competitors[["Competitor Brand", "Competitor Sales", "Competitor Market Share"]].drop_duplicates()

        # Aggregate values
    df_top_competitors = df_top_competitors.groupby("Competitor Brand", as_index=False).agg({
        "Competitor Sales": "max",
        "Competitor Market Share": "mean"
    })

    # Sort and select top 10 competitors
    df_top_competitors = df_top_competitors.sort_values(by="Competitor Sales", ascending=False).head(10)

    # Convert SOM to percentage and format to 2 decimal places
    df_top_competitors["Competitor Market Share"] = df_top_competitors["Competitor Market Share"] * 100
    df_top_competitors["Competitor Market Share"] = df_top_competitors["Competitor Market Share"].apply(lambda x: f"{x:.2f}%")
    df_top_competitors["Competitor Sales"] = df_top_competitors["Competitor Sales"].apply(lambda x: f"{x:,.2f}")  # Add commas and 2 decimal places
    
    # Convert all columns to strings for center alignment
    df_top_competitors = df_top_competitors.astype(str)

    # Custom CSS for dynamic dark/light mode styling
    st.markdown("""
        <style>
            /* Ensure visibility in dark mode */
            div[data-testid="stDataFrame"] {
                background-color: rgba(255, 255, 255, 0.1) !important; /* Transparent white for dark mode */
                color: white !important; /* White text for dark mode */
                border-radius: 10px;
            }
            div[data-testid="StyledDataFrame"] table {
                background-color: transparent !important; /* Keep table transparent */
                color: white !important; /* Keep text visible */
            }
        </style>
    """, unsafe_allow_html=True)

    # Format dataframe to look modern
    # st.dataframe(
    #     df_top_competitors.style.set_properties(**{
    #         'background-color': '#f8f9fa',
    #         'border': '1px solid black',
    #         'text-align': 'left'
    #     }),
    #     use_container_width=True
    # )

    df_top_competitors.reset_index(drop=True, inplace=True)
    df_top_competitors.index = range(1, len(df_top_competitors) + 1)
    # Display styled dataframe
    st.dataframe(df_top_competitors, use_container_width=True)

    
    # Display top competitor info
    if not df_top_competitors.empty:
        top_competitor = df_top_competitors.iloc[0]
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<h4>🏆 Top Competitor</h3>", unsafe_allow_html=True)
            st.markdown(f"<h5>{top_competitor['Competitor Brand']}</h5>", unsafe_allow_html=True)
        with col2:
            st.markdown("<h4>📊 Top Competitor SOM (%)</h3>", unsafe_allow_html=True)
            st.markdown(f"<h5>{top_competitor['Competitor Market Share']}</h5>", unsafe_allow_html=True)
    
    # ---- Competitor Pattern Analysis ----
    st.subheader("📊 Competitor Pattern Analysis")
    if not df_top_competitors.empty:
        selected_competitor = st.selectbox("Select Competitor", df_top_competitors["Competitor Brand"].unique())
        df_competitor_pattern = df_filtered[df_filtered["COMPETITOR_BRAND"] == selected_competitor]
        df_pattern_sales = df_competitor_pattern[["COMPETITOR_PATTERN", "COMPETITOR_PATTERN_SALES"]].drop_duplicates()
        if not df_pattern_sales.empty:
            fig_pattern_pie = px.pie(
                df_pattern_sales, 
                names="COMPETITOR_PATTERN", 
                values="COMPETITOR_PATTERN_SALES", 
                title=f"Sales Distribution by Pattern for {selected_competitor}",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            st.plotly_chart(fig_pattern_pie, use_container_width=True)
        else:
            st.warning("No pattern data available for the selected competitor.")
    
    # ---- Price Bar Chart ----
    st.subheader("💰 Price Comparison by Design")

    # Drop rows where 'SALES_PRICE_IN_USD' or 'DESIGN_NAME' is missing
    df_price_chart = df_filtered.dropna(subset=["SALES_PRICE_IN_USD", "DESIGN_NAME"])

    if not df_price_chart.empty:
        fig_price = px.bar(
            df_price_chart,
            x="DESIGN_NAME",
            y="SALES_PRICE_IN_USD",
            title="Price Comparison by Design",
            text=df_price_chart["SALES_PRICE_IN_USD"].apply(lambda x: f"${x:,.2f}"),  # Format text with dollar sign
            hover_data={"SALES_PRICE_IN_USD": True, "DESIGN_NAME": True, "BRAND_NAME": True, "BRAND_TYPE": True},
            color="BRAND_NAME",
            color_discrete_sequence=px.colors.qualitative.Set1
        )

        # Adjust axis labels
        fig_price.update_layout(
            xaxis_title="Design Name",
            yaxis_title="Sales Price in USD"
        )

        # Adjust text position so the longest bar has a visible label
        fig_price.update_traces(textposition="outside", cliponaxis=False)

        st.plotly_chart(fig_price, use_container_width=True)
    else:
        st.warning("No data available for the selected filters.")

    
    # ---- Car Parc Data ----
    st.subheader("🚘 Carparc Data")

    if not df_filtered.empty:
        carparc_data = df_filtered[["LUX_SUV_CARPARC", "TOTAL_CARPARC", "LUX_SUV_RATIO"]].drop_duplicates().iloc[0]

        st.markdown("""
            <style>
                .card {
                    background-color: #f8f8f8; /* Grey background */
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
                    width: 100%; /* Keep full width */
                    margin-bottom: 10px;
                }
                .icon {
                    font-size: 24px;
                }
                .title {
                    font-size: 20px;
                    font-weight: bold;
                    margin-bottom: 10px;
                    color: black; /* Ensure title is black */
                }
                .data-row {
                    display: flex;
                    justify-content: space-between;
                    font-size: 18px; /* Keep original size */
                    padding: 8px 0; /* Restore spacing */
                    color: black; /* Ensure text is black */
                }
                .highlight {
                    font-weight: bold;
                    color: #a370f0; /* Purple for values */
                }
            </style>
        """, unsafe_allow_html=True)

        st.markdown(f"""
            <div class="card">
                <div class="icon">🔹</div>
                <div class="title">Carparc Data</div>
                <div class="data-row">
                    <span>LUX SUV Carparc</span>
                    <span class="highlight">{carparc_data['LUX_SUV_CARPARC']:,.2f}</span>
                </div>
                <div class="data-row">
                    <span>Total Carparc</span>
                    <span class="highlight">{carparc_data['TOTAL_CARPARC']:,.2f}</span>
                </div>
                <div class="data-row">
                    <span>LUX SUV Ratio</span>
                    <span class="highlight">{carparc_data['LUX_SUV_RATIO']*100:.2f}%</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

    else:
        st.warning("No car parc data available for the selected filters.")

    
    # ---- Top 5 Fitments ----
    st.subheader("🛞 Top 5 Fitments")
    fitments = df_filtered["TOP_5_FITMENTS"].dropna().unique()
    for fitment in fitments[:5]:
        st.write(f"✅ {fitment}")
    
else:
    # DESKTOP LAYOUT - NEW CODE PROVIDED BY USER
    
    # ---- Industry & Goodyear Sales (Bar Chart) ----
    st.subheader("📊 Industry & Goodyear Sales")

    # Drop duplicates to ensure correct values
    sales_data = df_filtered[["TOTAL_INDUSTRY_SALES", "GOODYEAR_SALES"]].drop_duplicates().melt(var_name="Sales Type", value_name="Sales Value")

    # Rename for display only
    sales_type_mapping = {
        "TOTAL_INDUSTRY_SALES": "Total Industry Sales",
        "GOODYEAR_SALES": "Goodyear Sales"
    }
    sales_data["Sales Type"] = sales_data["Sales Type"].map(sales_type_mapping)

    fig_sales = px.bar(
        sales_data,
        x="Sales Type",
        y="Sales Value",
        title="Industry & Goodyear Sales",
        text_auto=True,
        color="Sales Type",
        color_discrete_map={
            "Total Industry Sales": "#1f77b4",  # Blue
            "Goodyear Sales": "#ffcc00"  # Yellow
        }
    )

    
    fig_sales.update_layout(
        xaxis_title="Sales Type",
        yaxis_title="Sales Value"
    )

    st.plotly_chart(fig_sales, use_container_width=True)

    # ---- Market Share ----
    st.subheader("📊 Market Share of Goodyear")

    # Drop duplicates to avoid miscalculations
    market_share = df_filtered[["SOM_OF_BRAND"]].drop_duplicates()["SOM_OF_BRAND"].mean()

    st.metric("Market Share (%)", f"{market_share * 100:.2f}%", help="Calculated based on SOM of the selected brand.")

    # ---- Competitor Sales ----
    st.subheader("🏆 Competitor Sales Comparison")

    # Drop duplicates to prevent incorrect bar lengths
    df_competitor_sales = (
        df_filtered[["COMPETITOR_BRAND", "COMPETITOR_BRAND_SALES"]]
        .drop_duplicates()
        .groupby("COMPETITOR_BRAND", as_index=False)
        .sum()
        .sort_values(by="COMPETITOR_BRAND_SALES", ascending=False)
        .head(10)  # Limit to top 35 competitors
    )

    fig_comp = px.bar(
        df_competitor_sales, 
        x="COMPETITOR_BRAND", 
        y="COMPETITOR_BRAND_SALES", 
        title="Top Competitor Sales", 
        text_auto=True,
        color_discrete_sequence=["#00CC96"]
    )

    fig_comp.update_layout(
        xaxis_title="Competitor brand",
        yaxis_title="Competitor brand sales",
        xaxis={'categoryorder': 'total descending'}
    )

    st.plotly_chart(fig_comp, use_container_width=True)

    # ---- Market Share Distribution (Brand Name Only) ----
    st.subheader("📊 Market Share Distribution")

    # Filter dataset to exclude missing brand names
    df_valid_brands = df_filtered.dropna(subset=["BRAND_NAME"])

    # Count occurrences of each brand
    brand_counts = df_valid_brands["BRAND_NAME"].value_counts().reset_index()
    brand_counts.columns = ["BRAND_NAME", "COUNT"]

    # Calculate percentage share
    total_brands = brand_counts["COUNT"].sum()
    brand_counts["PERCENTAGE"] = (brand_counts["COUNT"] / total_brands) * 100

    # Create pie chart with updated values
    fig_pie = px.pie(
        brand_counts, 
        names="BRAND_NAME", 
        values="PERCENTAGE", 
        title="Market Share Distribution",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )

    # Show percentage on hover
    fig_pie.update_traces(
        textinfo="label",  # Show only brand names on chart
        hovertemplate="<b>%{label}</b><br>Market Share: %{value:.2f}%"  # Show name & percentage on hover
    )

    st.plotly_chart(fig_pie, use_container_width=True)

    # ---- Top 10 Competitors Table ----
    st.subheader("🥇 Top 10 Competitors")

    # Rename columns
    df_top_competitors = df_filtered.rename(columns={
        "COMPETITOR_BRAND": "Competitor brand",
        "COMPETITOR_BRAND_SALES": "Competitor brand sales",
        "COMPETITOR_SOM_OF_BRAND": "Competitor market share"
    })

    df_top_competitors = df_top_competitors[["Competitor brand", "Competitor brand sales", "Competitor market share"]].drop_duplicates()

    # Aggregate values
    df_top_competitors = df_top_competitors.groupby("Competitor brand", as_index=False).agg({
        "Competitor brand sales": "max",
        "Competitor market share": "mean"
    })

    # Sort and limit to top 10
    df_top_competitors = df_top_competitors.sort_values(by="Competitor brand sales", ascending=False).head(10)

    # Format values
    df_top_competitors["Competitor market share"] = df_top_competitors["Competitor market share"] * 100
    df_top_competitors["Competitor market share"] = df_top_competitors["Competitor market share"].apply(lambda x: f"{x:.2f}%")
    df_top_competitors["Competitor brand sales"] = df_top_competitors["Competitor brand sales"].apply(lambda x: f"{x:,.2f}")  # Add commas and 2 decimal places

    # Convert all columns to strings for center alignment
    df_top_competitors = df_top_competitors.astype(str)

    # Display table with centered values
    # st.dataframe(
    #     df_top_competitors.style.set_properties(**{
    #         'background-color': '#f8f9fa',
    #         'border': '1px solid black',
    #         'text-align': 'center'
    #     }),
    #     use_container_width=True
    # )

    # Custom CSS for dynamic dark/light mode styling
    st.markdown("""
        <style>
            /* Ensure visibility in dark mode */
            div[data-testid="stDataFrame"] {
                background-color: rgba(255, 255, 255, 0.1) !important; /* Transparent white for dark mode */
                color: white !important; /* White text for dark mode */
                border-radius: 10px;
            }
            div[data-testid="StyledDataFrame"] table {
                background-color: transparent !important; /* Keep table transparent */
                color: white !important; /* Keep text visible */
            }
        </style>
    """, unsafe_allow_html=True)

    df_top_competitors.reset_index(drop=True, inplace=True)
    df_top_competitors.index = range(1, len(df_top_competitors) + 1)
    # Display styled dataframe
    st.dataframe(df_top_competitors, use_container_width=True)

    # ---- Top Competitor Name & Market Share ----
    if not df_top_competitors.empty:
        top_competitor = df_top_competitors.iloc[0]
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<h3>🏆 Top Competitor</h3>", unsafe_allow_html=True)
            st.markdown(f"<h5>{top_competitor['Competitor brand']}</h5>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("<h3>📊 Top Competitor SOM (%)</h3>", unsafe_allow_html=True)
            st.markdown(f"<h5>{top_competitor['Competitor market share']}</h5>", unsafe_allow_html=True)

    # ---- Competitor Pattern Pie Chart ----
    st.subheader("📊 Competitor Pattern Analysis")

    # Competitor selection filter from top 10 competitors
    selected_competitor = st.selectbox("Select Competitor", df_top_competitors["Competitor brand"].unique())

    # Filter dataset for selected competitor
    df_competitor_pattern = df_filtered[df_filtered["COMPETITOR_BRAND"] == selected_competitor]

    # Drop duplicates to ensure correct values
    df_pattern_sales = df_competitor_pattern[["COMPETITOR_PATTERN", "COMPETITOR_PATTERN_SALES"]].drop_duplicates()

    # Generate pie chart with correct values
    fig_pattern_pie = px.pie(
        df_pattern_sales, 
        names="COMPETITOR_PATTERN", 
        values="COMPETITOR_PATTERN_SALES", 
        title=f"Sales Distribution by Pattern for {selected_competitor}",
        color_discrete_sequence=px.colors.qualitative.Set3
    )

    st.plotly_chart(fig_pattern_pie, use_container_width=True)

    # ---- Price Bar Chart ----
    st.subheader("💰 Price Comparison by Design")

    # Drop rows where 'SALES_PRICE_IN_USD' or 'DESIGN_NAME' is missing
    df_price_chart = df_filtered.dropna(subset=["SALES_PRICE_IN_USD", "DESIGN_NAME"])

    if not df_price_chart.empty:
        fig_price = px.bar(
            df_price_chart,
            x="DESIGN_NAME",
            y="SALES_PRICE_IN_USD",
            title="Price Comparison by Design",
            text=df_price_chart["SALES_PRICE_IN_USD"].apply(lambda x: f"${x:,.2f}"),  # Format text with dollar sign
            hover_data={"SALES_PRICE_IN_USD": True, "DESIGN_NAME": True, "BRAND_NAME": True, "BRAND_TYPE": True},
            color="BRAND_NAME",
            color_discrete_sequence=px.colors.qualitative.Set1
        )

            # Adjust axis labels
        fig_price.update_layout(
            xaxis_title="Design Name",
            yaxis_title="Sales Price in USD"
        )

        # Adjust text position so the longest bar has a visible label
        fig_price.update_traces(textposition="outside", cliponaxis=False)

        st.plotly_chart(fig_price, use_container_width=True)
    else:
        st.warning("No data available for the selected filters.")

    
    # ---- Car Parc Data ----
    st.subheader("🚘 Carparc Data")

    if not df_filtered.empty:
        carparc_data = df_filtered[["LUX_SUV_CARPARC", "TOTAL_CARPARC", "LUX_SUV_RATIO"]].drop_duplicates().iloc[0]

        st.markdown("""
            <style>
                .card {
                    background-color: #f8f8f8; /* Grey background */
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
                    width: 100%; /* Keep full width */
                    margin-bottom: 10px;
                }
                .icon {
                    font-size: 24px;
                }
                .title {
                    font-size: 20px;
                    font-weight: bold;
                    margin-bottom: 10px;
                    color: black; /* Ensure title is black */
                }
                .data-row {
                    display: flex;
                    justify-content: space-between;
                    font-size: 18px; /* Keep original size */
                    padding: 8px 0; /* Restore spacing */
                    color: black; /* Ensure text is black */
                }
                .highlight {
                    font-weight: bold;
                    color: #a370f0; /* Purple for values */
                }
            </style>
        """, unsafe_allow_html=True)

        st.markdown(f"""
            <div class="card">
                <div class="icon">🔹</div>
                <div class="title">Carparc Data</div>
                <div class="data-row">
                    <span>LUX SUV Carparc</span>
                    <span class="highlight">{carparc_data['LUX_SUV_CARPARC']:,.2f}</span>
                </div>
                <div class="data-row">
                    <span>Total Carparc</span>
                    <span class="highlight">{carparc_data['TOTAL_CARPARC']:,.2f}</span>
                </div>
                <div class="data-row">
                    <span>LUX SUV Ratio</span>
                    <span class="highlight">{carparc_data['LUX_SUV_RATIO']*100:.2f}%</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

    else:
        st.warning("No car parc data available for the selected filters.")


    # ---- Top 5 Fitments ----
    st.subheader("🛞 Top 5 Fitments")
    fitments = df_filtered["TOP_5_FITMENTS"].dropna().unique()
    for fitment in fitments[:5]:
        st.write(f"✅ {fitment}")

# ---- Footer ----
st.markdown("***")
