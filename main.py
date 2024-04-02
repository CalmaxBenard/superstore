import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.figure_factory as ff

st.set_page_config(
    page_title="superstore",
    page_icon=":bar_chart:",
    layout="wide"
)
st.title(":earth_americas: Apex Superstore EDA")
st.markdown("<style>div.block-container{padding-top:1.3rem}</style>", unsafe_allow_html=True)

file = st.file_uploader(":file_folder: Upload File", type=["csv", "txt", "xlsx", "xls"])

if file is not None:
    filename = file.name
    st.write(filename)
    df = pd.read_csv(filename, encoding='unicode_escape')
else:
    df = pd.read_csv("superstore.csv", encoding='unicode_escape')

# Reformat date to datetime object
col1, col2 = st.columns(2)
df["Order Date"] = pd.to_datetime(df["Order Date"], format="mixed")

# Define start and end dates for the analysis
start_date = df["Order Date"].min()
end_date = df["Order Date"].max()

# Display dates
with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", start_date))

with col2:
    date2 = pd.to_datetime(st.date_input("End Date", end_date))

# Filter dataframe to include only selected dates(duration)
df = df[(df["Order Date"] >= start_date) & (df["Order Date"] <= end_date)].copy()

# Create sidebar
st.sidebar.header("Filter Data")

# Filter by Region
region = st.sidebar.multiselect("Pick a Region", df["Region"].unique())
if not region:
    df2 = df.copy()
else:
    df2 = df[df["Region"].isin(region)]

# Filter by State
state = st.sidebar.multiselect("Pick a State", df2["State"].unique())
if not state:
    df3 = df2.copy()
else:
    df3 = df2[df2["State"].isin(state)]

# Filter by City
city = st.sidebar.multiselect("Pick a City", df3["City"].unique())

# Applying Filters
if not region and not state and not city:
    filtered_df = df
elif not state and not city:
    filtered_df = df[df["Region"].isin(region)]
elif not region and not city:
    filtered_df = df[df["State"].isin(state)]
elif state and city:
    filtered_df = df3[(df3["State"].isin(state)) & (df3["City"].isin(city))]
elif region and city:
    filtered_df = df3[(df3["Region"].isin(region)) & (df3["City"].isin(city))]
elif region and state:
    filtered_df = df3[(df3["Region"].isin(region)) & (df3["State"].isin(state))]
elif city:
    filtered_df = df3[df3["City"]]
else:
    filtered_df = df3[df3["Region"].isin(region) & df3["State"].isin(state) & df3["City"].isin(city)]

# Categorize Data
cat_df = filtered_df.groupby(by=["Category"], as_index=False)

# Get total sales from categories
sales = cat_df["Sales"].sum()

# Bar plot of the sales per category
with col1:
    st.subheader("Sales per Category")
    fig = px.bar(sales, x="Category", y="Sales", template="seaborn",
                 text=["${:,.2f}".format(sale) for sale in sales["Sales"]])
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Sales per Region")
    fig = px.pie(filtered_df, values="Sales", names="Region", hole=0.2)
    fig.update_traces(text=filtered_df["Region"], textposition="inside")
    st.plotly_chart(fig, use_container_width=True)

cl1, cl2 = st.columns(2)
with cl1:
    with st.expander("View Category Data"):
        st.write(sales)
        csv = sales.to_csv(index=False).encode("utf-8")
        st.download_button("Download Data", data=csv, file_name="category.csv", mime="text/csv",
                           help="Click here to download CSV file.")

with cl2:
    with st.expander("View Regional Data"):
        region = filtered_df.groupby(by="Region", as_index=False)["Sales"].sum()
        st.write(region)
        csv = region.to_csv(index=False).encode("utf-8")
        st.download_button("Download Data", data=csv, file_name="region.csv", mime="txt/csv")

# Time Series
filtered_df["month_year"] = filtered_df["Order Date"].dt.to_period("M")
time_df = pd.DataFrame(filtered_df.groupby(filtered_df["month_year"].dt.strftime("%b-%Y"))["Sales"].sum()).reset_index()
fig2 = px.line(time_df, x="month_year", y="Sales", labels={"Sales": "Amount"}, template="gridon")
st.subheader("Time Series Analysis")
st.plotly_chart(fig2, use_container_width=True)

with st.expander("View Time-Series Data"):
    st.write(time_df)

# A tree map based on region, category, sub-category
st.subheader("Hierarchical View od Sales")
fig3 = px.treemap(filtered_df, path=["Region", "Category", "Sub-Category"], values="Sales",
                  hover_data=["Sales"], color="Sub-Category")
st.plotly_chart(fig3, use_container_width=True)

# Sales charts
chart1, chart2 = st.columns(2)
with chart1:
    st.subheader("Segment Sales")
    fig = px.pie(filtered_df, values="Sales", names="Segment", template="plotly_dark")
    fig.update_traces(text=filtered_df["Segment"], textposition="inside")
    st.plotly_chart(fig, use_container_width=True)
with chart2:
    st.subheader("Category Sales")
    fig = px.pie(filtered_df, values="Sales", names="Category", template="gridon")
    fig.update_traces(text=filtered_df["Category"], textposition="inside")
    st.plotly_chart(fig, use_container_width=True)

# Monthly sales summary
st.subheader(":point_right: Monthly Sales Summary")
with st.expander("Summary Table"):
    table_df = df[:10][["Region", "State", "City", "Category", "Sales", "Profit", "Quantity"]]
    fig = ff.create_table(table_df, colorscale="balance")
    st.plotly_chart(fig, use_container_width=True)

    # Sub category sales per month
    st.markdown("Monthly Sub-Category Sales")
    filtered_df["month"] = filtered_df["Order Date"].dt.month_name()
    sub_cat_df = pd.pivot_table(filtered_df, values="Sales", index="Sub-Category", columns="month")
    st.write(sub_cat_df)

# scatterplot
data = px.scatter(filtered_df, x="Sales", y="Profit", size="Quantity", color=filtered_df.Category)
data["layout"].update(
    title="Relationship between Sales and Profit sized by Quantity",
    titlefont=dict(size=20), xaxis=dict(title="Sales", titlefont=dict(size=18)),
    yaxis=dict(title="Profit", titlefont=dict(size=18))
)
st.plotly_chart(data, use_container_width=True)

# data used
st.subheader("Overview of the Data Used")
with st.expander("View Data"):
    st.write(filtered_df.iloc[:500, 1:20:2])

# download original dataset
st.write("Download Dataset used in the Project in here :point_down:")
csv = df.to_csv(index=False).encode("utf-8")
st.download_button("Download Data", data=csv, file_name="Data.csv", mime="txt/csv")