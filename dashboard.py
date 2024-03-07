import streamlit as st
import plotly
import plotly.express as px
import pandas as pd 
import numpy as np
import math
import random
import os
import warnings
import matplotlib.pyplot 
import matplotlib
import matplotlib.cm as cm
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Dashboard Superstore", page_icon=":bar_chart:", layout="wide")

#---------------------Memberikan title
st.title(" :bar_chart: Dashboard Sederhana SuperStore")

st.markdown('<style>div.block-container{padding-top:lrem;}</style>', unsafe_allow_html=True)
#---------------------Menambahkan file upload
f1 = st.file_uploader("Masukkan File",type =(["csv","txt","xlsx","xls"])) 
if f1 is not None:
    filename = f1.name
    st.write(filename)
    
    # Cek tipe file yang diunggah
    if filename.endswith('.csv'):
        df = pd.read_csv(f1, sep='t')  # Jika format file adalah .csv, gunakan sep='\t' untuk menggunakan tab sebagai separator
    else:
        df = pd.read_excel(f1)

    st.success('File berhasil diunggah!')
else:
    url = "https://raw.githubusercontent.com/FerdyPut/Dashboard-SuperStore/main/Superstore.xlsx"
    df = pd.read_excel(url)
#---------------------------Masuk ke Proses Picker atau Filter
# MEMBUAT TANGGAL

col1, col2 = st.columns((2))
df["Order Date"] = pd.to_datetime(df['Order Date'])

startDate = pd.to_datetime(df["Order Date"]).min()
endDate = pd.to_datetime(df["Order Date"]).max()

with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))
with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))

df = df[(df["Order Date"] >= date1) & (df["Order Date"] <= date2)].copy()

#MEMBUAT FILTER REGION

st.sidebar.header("Silahkan memilih: ")
region = st.sidebar.multiselect("Pilih Region", df["Region"].unique())
if not region:
    df2 = df.copy()
else:
    df2 = df[df["Region"].isin(region)]   

#MEMBUAT FILTER NEGARA
state = st.sidebar.multiselect("Pilih Negara", df2['State'].unique())
if not state:
    df3 = df2.copy()
else:
    df3 = df2[df2["State"].isin(state)]  

#MEMBUAT FILTER KOTA

city = st.sidebar.multiselect("Pilih Kota", df3['City'].unique())
if not city:
    df4 = df3.copy()
else:
    df4 = df3[df3["City"].isin(city)]

# FILTER KALAU GAK MEMILIH FILTER REGION, STATE, DAN CITY
#---muncul data semua
if not region and not state and not city:
    filter_df = df
#---muncul data region saja
elif not state and not city:
    filter_df = df[df["Region"].isin(region)]
#---muncul data state saja
elif not region and not city:
    filter_df = df[df["State"].isin(state)]
#---muncul data city saja
elif not state and not region:
    filter_df = df[df["City"].isin(city)]
#---muncul data city dan region saja
elif state and city:
    filter_df = df[df["City"].isin(city) & df["Region"].isin(region)]
#---muncul data city dan region saja
elif state and city:
    filter_df = df[df["City"].isin(city) & df["State"].isin(state)]
    #---muncul data city dan region saja
elif region and city:
    filter_df = df[df["Region"].isin(region) & df["Region"].isin(region)]
#---muncul data city dan region saja
elif region and state:
    filter_df = df[df["Region"].isin(region) & df["State"].isin(state)]
elif city:
    filter_df = df[df["City"].isin(city)]
else:
    filter_df = df[df["Region"].isin(region) & df["State"].isin(state)& df["City"].isin(city)]

#---------PROSES VISUALISASI
#--- Pie Chart dan Barchart
category_df = filter_df.groupby(by = ["Category"], as_index = False)["Sales"].sum()

with col1:
    st.markdown("<h3 style='text-align: center;'>Kategori Terhadap Sales</h3>", unsafe_allow_html=True)
    fig = px.bar(category_df, x= "Category", y="Sales", text = ['${:,.2f}'.format(x) for x in category_df["Sales"]],
                 template = "seaborn")
    st.plotly_chart(fig,use_container_width=True, height=200)

with col2:
    st.markdown("<h3 style='text-align: center;'>Region Terhadap Sales</h3>", unsafe_allow_html=True)
    fig= px.pie(filter_df, values ="Sales", names= "Region", hole=0.5)
    fig.update_traces(text = filter_df["Region"], textposition = "outside")
    st.plotly_chart(fig,use_container_width=True)

#Button buat Download Data
# memakai with atau cl1 dan cl2 itu buat membagi kolom karena kan ada 2 kolom buat button download data
cl1,cl2 = st.columns(2)
with cl1:
    with st.expander("Category_ViewData"):
        st.write(category_df.style.background_gradient(cmap="Blues"))
        csv = category_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data", data = csv, file_name = "Category.csv", mime= "text/csv",
        help="Click here to dowload the data as a CSV file")
with cl2:
    with st.expander("Region_ViewData"):
        region = filter_df.groupby(by="Region", as_index = False)["Sales"].sum()
        st.write(region.style.background_gradient(cmap="Oranges"))
        csv = region.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data", data = csv, file_name = "Region.csv", mime= "text/csv",
        help="Click here to dowload the data as a CSV file")

#-----Linechart atau Time Series
filter_df['month_year'] = filter_df["Order Date"].dt.to_period("M")
st.subheader("Time Series Analysis")

linechart = pd.DataFrame(filter_df.groupby(filter_df['month_year'].dt.strftime("%Y: %b"))["Sales"].sum()).reset_index()
fig2 = px.line(linechart, x= "month_year", y="Sales", labels = {"Sales": "Jumlah"}, height= 500, width = 1000, template ="gridon")
st.plotly_chart(fig2, use_container_width=True)

#Download Data
with st.expander("Data Time Series Overview"):
    st.write(linechart.style.background_gradient(cmap="Blues"))
    csv = linechart.to_csv(index=False).encode('utf-8')
    st.download_button("Download Data", data = csv, file_name = "Data Time Series.csv", mime= "text/csv",
    help="Click here to dowload the data as a CSV file")

#----- Treemap
st.subheader("Treemap Sales")
fig3 = px.treemap(filter_df, path = ["Region", "Category", "Sub-Category"], values ="Sales", hover_data= ["Sales"],
                  color = "Sub-Category")
fig3.update_layout(width = 800, height = 650)
st.plotly_chart(fig3, use_container_width=True)

#----- Segment dan kategori dijadikan Piechart
chart1, chart2 = st.columns((2))
with chart1:
    st.subheader("Segment Terhadap Sales")
    fig = px.pie(filter_df, values = "Sales", names = "Segment", template = "plotly_dark")
    fig.update_traces(text = filter_df["Segment"], textposition = "inside")
    st.plotly_chart(fig, use_container_width= True)
with chart2:
    st.subheader("Kategori Terhadap Sales")
    fig = px.pie(filter_df, values = "Sales", names = "Category", template = "gridon")
    fig.update_traces(text = filter_df["Category"], textposition = "inside")
    st.plotly_chart(fig, use_container_width= True)

import plotly.figure_factory as ff
st.subheader(":point_right: Month Terhadap Sub-Category Sales Summary")
with st.expander("Summary Table"):
    df_sample = df[0:10][["Region", "State", "City", "Category", "Sales", "Profit", "Quantity"]]
    fig = ff.create_table(df_sample, colorscale="cividis")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("Month Terhadap Sub-Category Table")
    filter_df["month"] = filter_df["Order Date"].dt.month_name()
    sub_category_year = pd.pivot_table(data = filter_df , values ="Sales",
                                       index = ["Sub-Category"], columns = "month")
    st.write(sub_category_year.style.background_gradient(cmap= "Blues"))


#--- Scatterplot
data1 = px.scatter(filter_df, x = "Sales", y = "Profit", size = "Quantity")
data1["layout"].update(title="Hubungan antara Sales dan Profit Dengan ScatterPlot",
                       titlefont = dict(size=2), xaxis = dict(title="Sales", titlefont = dict(size=19)),
                       yaxis = dict(title= "Profit", titlefont = dict(size=19)))

st.plotly_chart(data1, use_container_width=True)
#Download Data
with st.expander("Data Original Overview"):
    st.write(filter_df.iloc[:500,1:20:2].style.background_gradient(cmap="Oranges"))


csv = df.to_csv(index=False).encode('utf-8')
st.download_button("Download Data Original", data = csv, file_name = "Data Original.csv", mime= "text/csv",
help="Click here to dowload the data as a CSV file")
