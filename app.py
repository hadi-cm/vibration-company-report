
python
import streamlit as st
import pandas as pd
import numpy as np

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
    try:
        df = pd.read_csv(SHEET_URL)
        # حذف هدرهای تکراری (مثل ردیف 14)
        df = df[df['تاریخ'].astype(str).str.contains('تاریخ') == False]
        # پر کردن ردیف‌های خالی برای تجهیزات و خطوط
        cols_to_fill = ['تاریخ', 'خط تولید', 'واحد', 'عنوان تجهیز']
        df[cols_to_fill] = df[cols_to_fill].ffill()
        return df
    except Exception as e:
        st.error(f"خطا در اتصال به گوگل شیت: {e}")
        return None

# تابع رنگ‌بندی اعداد ارتعاشات
def color_vibration_values(val):
    try:
        num = float(val)
        if num > 7.2:
            return 'background-color: #ffcccc; color: black' # قرمز
        elif num >= 4.7:
            return 'background-color: #ffffcc; color: black' # زرد
        else:
            return 'background-color: white; color: black' # سفید
    except:
        return ''

# تابع رنگ‌بندی ستون وضعیت (متنی)
def color_status_text(val):
    if 'هشدار' in str(val):
        return 'background-color: #ffcccc; color: black'
    if 'مراقبت' in str(val):
        return 'background-color: #ffffcc; color: black'
    if 'نرمال' in str(val):
        return 'background-color: #ccffcc; color: black'
    return ''

try:
    df = load_data()
except Exception as e:
    st.error(f"خطا در بارگذاری داده‌ها: {e}")
    st.stop()

if df is not None:
    st.sidebar.header("🔍 فیلترهای گزارش")
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
            st.subheader(f"🏢 خط تولید: {line}")
            for eq in line_df['عنوان تجهیز'].dropna().unique():
                eq_df = line_df[line_df['عنوان تجهیز'] == eq]
                st.markdown(f"📦 تجهیز: {eq} | واحد:* {eq_df['واحد'].iloc[0]}")
                # ستون‌های مورد نظر برای نمایش
                cols = ['محل اندازه گیری', 'عمودی', 'افقی', 'محوری', 'وضعیت']
                available_cols = [c for c in cols if c in eq_df.columns]
                # اعمال رنگ‌بندی روی اعداد و وضعیت
                def apply_custom_styles(x):
                    # ابتدا یک کپی از استایل می‌گیریم
                    style_df = pd.DataFrame('', index=x.index, columns=x.columns)
                    # رنگ‌بندی ستون‌های عددی
                    for col in ['عمودی', 'افقی', 'محوری']:
                        if col in x.columns:
                            style_df[col] = x[col].apply(color_vibration_values)
                    # رنگ‌بندی ستون وضعیت
                    if 'وضعیت' in x.columns:
                        style_df['وضعیت'] = x['وضعیت'].apply(color_status_text)
                    return style_df
                styled = eq_df[available_cols].style.apply(apply_custom_styles, axis=None)
                st.dataframe(styled, use_container_width=True)
                st.markdown("---")
st.markdown("---")
st.caption(f"تمامی حقوق متعلق به {COMPANY_NAME} است | طراحی و توسعه توسط: هادی")
