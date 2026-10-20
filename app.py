import streamlit as st
import pandas as pd
# تنظیمات صفحه
st.set_page_config(page_title="سامانه پایش ارتعاشات - فاز فیدار پارسیان", layout="wide")
# --- بخش لوگو و نام شرکت (نسخه خلوت و حرفه‌ای) ---
try:
    col1, col2, col3 = st.columns([1, 2, 1]) 
    with col2:
        # نمایش لوگو (نام فایل را اگر jpg است تغییر دهید)
        st.image("logo.png", use_container_width=True) 
except:
    st.warning("فایل لوگو یافت نشد. لطفاً نام فایل را در گیت‌هاب چک کنید.")
# عنوان سامانه درست زیر لوگو
st.markdown("<p style='text-align: center; font-size: 20px; font-weight: bold; color: #555555;'>📊 سامانه هوشمند پایش وضعیت ارتعاشات تجهیزات</p>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888888;'>توسعه‌دهنده: هادی</p>", unsafe_allow_html=True)
st.divider()
# ----------------------------------------------
# آدرس گوگل شیت
SHEET_URL = "https://docs.google.com/spreadsheets/d/1H4Yf3ilu72hI7YZns6EXNMpOfH-EII98_sEO_81uXrs/export?format=csv&gid=0"
@st.cache_data(ttl=60)
def load_data():
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = ['تاریخ', 'خط تولید', 'واحد', 'عنوان تجهیز', 'محل اندازه گیری', 'عمودی', 'افقی', 'محوری', 'واحد اندازه گیری', 'توضیحات', 'وضعیت']
        df = df[~df['تاریخ'].astype(str).str.contains('تاریخ')]
        cols_to_fill = ['تاریخ', 'خط تولید', 'واحد', 'عنوان تجهیز']
        df[cols_to_fill] = df[cols_to_fill].ffill()
        for c in ['عمودی', 'افقی', 'محوری']:
            df[c] = pd.to_numeric(df[c], errors='coerce')
        return df
    except Exception as e:
        st.error(f"خطا در خواندن داده‌ها: {e}")
        return None
def color_vibration(val):
    if pd.isna(val): return ''
    if val > 7.2: return 'background-color: #ffcccc; color: black'
    if val >= 4.7: return 'background-color: #ffffcc; color: black'
    return ''
def color_status_text(val):
    val_str = str(val)
    if 'هشدار' in val_str: return 'background-color: #ffcccc; color: black'
    if 'مراقبت' in val_str: return 'background-color: #ffffcc; color: black'
    if 'نرمال' in val_str: return 'background-color: #ccffcc; color: black'
    return ''
df = load_data()
if df is not None:
    all_lines = df['خط تولید'].dropna().unique().tolist()
    selected_lines = st.sidebar.multiselect("انتخاب خط تولید", all_lines, default=all_lines)
    for line in selected_lines:
        line_data = df[df['خط تولید'] == line]
        st.header(f"🏢 {line}")
        for eq in line_data['عنوان تجهیز'].unique():
            eq_data = line_data[line_data['عنوان تجهیز'] == eq].dropna(subset=['عمودی', 'افقی', 'محوری'], how='all')
            if eq_data.empty: continue
            st.subheader(f"📦 تجهیز: {eq}")
            display_cols = ['محل اندازه گیری', 'عمودی', 'افقی', 'محوری', 'وضعیت']
            styled_df = eq_data[display_cols].style.format({
                'عمودی': "{:.1f}", 
                'افقی': "{:.1f}", 
                'محوری': "{:.1f}"
            }, na_rep="-").map(color_vibration, subset=['عمودی', 'افقی', 'محوری']).map(color_status_text, subset=['وضعیت'])
            st.dataframe(styled_df, use_container_width=True, hide_index=True)
            st.write("---")
st.caption("تمامی حقوق متعلق به شرکت فاز فیدار پارسیان می‌باشد.")
