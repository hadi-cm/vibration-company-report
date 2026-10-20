import streamlit as st
import pandas as pd

st.set_page_config(page_title="سامانه گزارش ارتعاشات", layout="wide")

COMPANY_NAME = "نام شرکت شما"
st.title(COMPANY_NAME)
st.caption("سامانه هوشمند پایش وضعیت ارتعاشات")
st.divider()

SHEET_URL = "https://docs.google.com/spreadsheets/d/1H4Yf3ilu72hI7YZns6EXNMpOfH-EII98_sEO_81uXrs/export?format=csv&gid=0"

@st.cache_data(ttl=60
   
@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(SHEET_URL)
    df.columns = ['تاریخ', 'خط تولید', 'واحد', 'عنوان تجهیز', 'محل اندازه گیری', 'عمودی', 'افقی', 'محوری', 'واحد اندازه گیری', 'توضیحات', 'وضعیت']
    df = df[~df['تاریخ'].astype(str).str.contains('تاریخ')]
    cols_to_fill = ['تاریخ', 'خط تولید', 'واحد', 'عنوان تجهیز']
    df[cols_to_fill] = df[cols_to_fill].ffill()
    return df
           
    df = pd.read_csv(SHEET_URL)
    df.columns = df.columns.str.strip()
    st.write(list(df.columns))
    df = df[~df['تاریخ'].astype(str).str.contains('تاریخ')]
    cols_to_fill = ['تاریخ', 'خط تولید', 'واحد', 'عنوان تجهیز']
    df[cols_to_fill] = df[cols_to_fill].ffill()
    return df

def color_vibration(val):
    try:
        num = float(val)
    except:
        return ''
    if num > 7.2:
        return 'background-color: #ffcccc; color: black'
    elif num >= 4.7:
        return 'background-color: #ffffcc; color: black'
    return 'background-color: white; color: black'

df = load_data()

for line in df['خط تولید'].dropna().unique():
    st.subheader(f"🏢 خط تولید: {line}")
    line_df = df[df['خط تولید'] == line]
    for eq in line_df['عنوان تجهیز'].dropna().unique():
        eq_df = line_df[line_df['عنوان تجهیز'] == eq]
        st.markdown(f"📦 تجهیز:* {eq}")
        cols = [c for c in ['محل اندازه گیری', 'عمودی', 'افقی', 'محوری', 'وضعیت'] if c in eq_df.columns]
        styled = eq_df[cols].style.map(color_vibration, subset=[c for c in ['عمودی', 'افقی', 'محوری'] if c in cols])
        st.dataframe(styled, use_container_width=True)
        st.markdown()
