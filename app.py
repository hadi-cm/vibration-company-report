import streamlit as st
import pandas as pd
# ۱. تنظیمات صفحه
st.set_page_config(page_title="سامانه گزارش ارتعاشات اختصاصی", layout="wide")
# ۲. استایل‌دهی پیشرفته برای ظاهر شرکتی و شخصی
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .company-header {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 15px;
        border-bottom: 4px solid #007bff;
        margin-bottom: 30px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.05);
        display: flex;
        align-items: center;
    }
    .company-name {
        font-size: 34px;
        font-weight: bold;
        color: #1e3a8a;
        margin-right: 20px;
        font-family: 'Tahoma', sans-serif;
    }
    .designer-footer {
        text-align: center;
        padding: 20px;
        color: #6c757d;
        font-size: 14px;
        border-top: 1px solid #dee2e6;
        margin-top: 50px;
    }
    .designer-name {
        color: #007bff;
        font-weight: bold;
        font-size: 16px;
        text-decoration: none;
    }
    </style>
    """, unsafe_allow_html=True)
# ۳. بخش سربرگ (لوگو و نام شرکت)
LOGO_URL = "https://via.placeholder.com/80" # <--- لینک لوگوی شرکت را اینجا بگذار
COMPANY_NAME = "نام شرکت شما" # <--- نام شرکت را اینجا بنویس
col1, col2 = st.columns([1, 5])
with col1:
    st.image(LOGO_URL, width=100)
with col2:
    st.markdown(f"<div class='company-name'>{COMPANY_NAME}</div>", unsafe_allow_html=True)
    st.markdown("<p style='margin-top:-20px; color:gray; font-size:18px;'>سامانه هوشمند پایش وضعیت ارتعاشات</p>", unsafe_allow_html=True)
st.divider()
# ۴. اتصال به گوگل شیت
SHEET_URL = "https://docs.google.com/spreadsheets/d/1H4Yf3ilu72hI7YZns6EXNMpOfH-EII98_sEO_81uXrs/export?format=csv&gid=0"
def load_data():
    try:
        df = pd.read_csv(SHEET_URL)
        cols_to_fill = ['تاریخ', 'خط تولید', 'واحد', 'عنوان تجهیز']
        df[cols_to_fill] = df[cols_to_fill].ffill()
        return df
    except Exception as e:
        st.error(f"خطا در اتصال به گوگل شیت: {e}")
        return None
# ۵. منطق اصلی برنامه
df = load_data()
if df is not None:
    st.sidebar.header("🔍 فیلترهای گزارش")
    lines = df['خط تولید'].unique().tolist()
    selected_line = st.sidebar.multiselect("انتخاب خط تولید", lines, default=lines)
    units = df['واحد'].unique().tolist()
    selected_unit = st.sidebar.multiselect("انتخاب واحد", units, default=units)
    filtered_df = df[(df['خط تولید'].isin(selected_line)) & (df['واحد'].isin(selected_unit))]
    if not filtered_df.empty:
        for line in selected_line:
            line_df = filtered_df[filtered_df['خط تولید'] == line]
            if not line_df.empty:
                st.subheader(f"🏢 خط تولید: {line}")
                equipments = line_df['عنوان تجهیز'].unique()
                for eq in equipments:
                    eq_df = line_df[line_df['عنوان تجهیز'] == eq].copy()
                    unit_name = eq_df['واحد'].iloc[0]
                    st.markdown(f"**📦 تجهیز:** {eq} | *واحد: {unit_name}")

                    def color_status(val):
                        if 'هشدار' in str(val): return 'background-color: #ffcccc'
                        if 'مراقبت' in str(val): return 'background-color: #ffffcc'
                        if 'نرمال' in str(val): return 'background-color: #ccffcc'
                        return ''

                    styled_df = eq_df[['محل اندازه گیری', 'عمودی', 'افقی', 'محوری', 'وضعیت']].style.applymap(color_status, subset=['وضعیت'])
                    st.dataframe(styled_df, use_container_width=True)
                    st.markdown("---")
    else:
        st.warning("داده‌ای یافت نشد.")
else:
    st.error("خطا در بارگذاری داده‌ها.")

# ۶. بخش امضای دیجیتال (برای تبلیغات و اعتبار هادی)
st.markdown(f"""
    <div class='designer-footer'>
        <p>تمامی حقوق مادی و معنوی متعلق به <b>{COMPANY_NAME}</b> است.</p>
        <p>🚀 طراحی، تحلیل و توسعه سیستم توسط: <span class='designer-name'>هادی</span></p>
    </div>
  unsafe_allow_html=True)
