import streamlit as st
import pandas as pd

st.set_page_config(page_title="سامانه گزارش ارتعاشات", layout="wide")

LOGO_URL = "https://via.placeholder.com/80"
COMPANY_NAME = "نام شرکت شما"

col1, col2 = st.columns([1, 5])
with col1:
    st.image(LOGO_URL, width=100)
with col2:
    st.title(COMPANY_NAME)
    st.caption("سامانه هوشمند پایش وضعیت ارتعاشات")

st.divider()

SHEET_URL = "https://docs.google.com/spreadsheets/d/1H4Yf3ilu72hI7YZns6EXNMpOfH-EII98_sEO_81uXrs/export?format=csv&gid=0"

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv(SHEET_URL)
    cols_to_fill = ['تاریخ', 'خط تولید', 'واحد', 'عنوان تجهیز']
    df[cols_to_fill] = df[cols_to_fill].ffill()
    return df

def color_status(val):
    if 'هشدار' in str(val):
        return 'background-color: #ffcccc'
    if 'مراقبت' in str(val):
        return 'background-color: #ffffcc'
    if 'نرمال' in str(val):
        return 'background-color: #ccffcc'
    return ''

try:
    df = load_data()
except Exception as e:
    st.error(f"خطا در اتصال به گوگل شیت: {e}")
    st.stop()

st.sidebar.header("فیلترهای گزارش")
lines = df['خط تولید'].dropna().unique().tolist()
selected_line = st.sidebar.multiselect("انتخاب خط تولید", lines, default=lines)
units = df['واحد'].dropna().unique().tolist()
selected_unit = st.sidebar.multiselect("انتخاب واحد", units, default=units)

filtered_df = df[df['خط تولید'].isin(selected_line) & df['واحد'].isin(selected_unit)]

if filtered_df.empty:
    st.warning("داده‌ای یافت نشد.")
else:
    for line in selected_line:
        line_df = filtered_df[filtered_df['خط تولید'] == line]
        if line_df.empty:
            continue
        st.subheader(f"خط تولید: {line}")
        for eq in line_df['عنوان تجهیز'].dropna().unique():
            eq_df = line_df[line_df['عنوان تجهیز'] == eq]
            st.markdown(f"تجهیز: {eq} | واحد: {eq_df['واحد'].iloc[0]}")
            styled = eq_df[['محل اندازه گیری', 'عمودی', 'افقی', 'محوری', 'وضعیت']].style.map(color_status, subset=['وضعیت'])
            st.dataframe(styled, use_container_width=True)
            st.markdown("---")

st.markdown("---")
st.caption(f"تمامی حقوق متعلق به {COMPANY_NAME} است | طراحی و توسعه توسط: هادی")
