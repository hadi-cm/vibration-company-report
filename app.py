import pandas as pd
import streamlit as st
import base64
# ==============================================================================
# 1. تنظیمات اولیه صفحه (Page Config)
# ==============================================================================
st.set_page_config(
    page_title="داشبورد ارتعاشات سیمان تهران - مهندس هادی زندیه", 
    layout="wide"
)
# تابع برای خواندن عکس‌های محلی و تبدیل به فرمت قابل نمایش در HTML
def get_image_base64(path):
    try:
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except:
        return ""
# تبدیل لوگوها
logo_siman_base64 = get_image_base64("client_logo.png")
logo_faz_fidar_base64 = get_image_base64("my_logo.png")
# استایل CSS برای راست‌چین کردن (RTL)، لوگوها و فوتر
st.markdown("""
    <style>
    .main {
        direction: rtl;
        text-align: right;
    }
    div[data-testid="stMetricValue"] {
        text-align: right;
    }
    .stDataFrame {
        direction: rtl;
    }
    .logo-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
        background-color: white;
        padding: 10px;
        border-radius: 10px;
    }
    .logo-img {
        width: 100px;
        height: auto;
    }
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #f8f9fa;
        color: #333;
        text-align: center;
        padding: 12px 0;
        font-weight: bold;
        font-size: 16px;
        border-top: 3px solid #2E7D32;
        z-index: 999;
    }
    </style>
    """, unsafe_allow_html=True)
# ==============================================================================
# 2. بخش لوگوها و عنوان (Header)
# ==============================================================================
st.markdown(f"""
    <div class="logo-container">
        <img src="data:image/png;base64,{logo_faz_fidar_base64}" class="logo-img">
        <h1 style='text-align: center; flex-grow: 1; color: #1E3A8A; font-size: 28px;'>📊 داشبورد جامع پایش ارتعاشات و بالانس - سیمان تهران</h1>
        <img src="data:image/png;base64,{logo_siman_base64}" class="logo-img">
    </div>
    """, unsafe_allow_html=True)
st.markdown("---")
# ==============================================================================
# 3. اتصال به منبع داده (لینک منتشر شده گوگل شیت)
# ==============================================================================
sheet_url = "https://docs.google.com/spreadsheets/d/1H4Yf3ilu72hl7YZns6EXNMpOfh-Eli98_sEO_81uXrs/pub?output=csv"
@st.cache_data(ttl=60)
def load_data(url):
    try:
        df = pd.read_csv(url)
        return df
    except Exception as e:
        return None
df = load_data(sheet_url)
if df is not None:
    st.success("✅ اطلاعات با موفقیت به‌روزرسانی شد!")
    # ==============================================================================
    # 4. بخش نمایش جدول داده‌ها
    # ==============================================================================
    st.subheader("📋 جدول جامع داده‌های ارتعاشات و بالانس")
    st.dataframe(df, use_container_width=True)
    # ==============================================================================
    # 5. بخش شاخص‌های کلیدی (Metrics)
    # ==============================================================================
    st.markdown("---")
    st.subheader("📈 شاخص‌های کلیدی")
    col1, col2 = st.columns(2)
    with col1:
        if "بالانس" in df.columns:
            balance_numeric = pd.to_numeric(df["بالانس"], errors='coerce').fillna(0)
            total_balance = balance_numeric.sum()
            st.metric(label="جمع کل بالانس‌ها (کل دوره)", value=f"{total_balance:.2f}")
    with col2:
        if "mm/s" in df.columns:
            vibration_numeric = pd.to_numeric(df["mm/s"], errors='coerce')
            max_vibe = vibration_numeric.max()
            st.metric(label="حداکثر ارتعاش ثبت شده (mm/s)", value=f"{max_vibe:.2f}")
    # ==============================================================================
    # 6. بخش گزارش جمع سالانه (بر اساس ستون اول: تاریخ)
    # ==============================================================================
    st.markdown("---")
    st.subheader("📅 گزارش جمع بالانس سالانه")
    date_column = "تاریخ" 
    if date_column in df.columns:
        try:
            df_copy = df.copy()
            df_copy[date_column] = df_copy[date_column].ffill()
            df_copy['Year'] = df_copy[date_column].astype(str).str.split('/').str[-1].str.strip()
            years = df_copy['Year'].unique().tolist()
            if years and years[0] != 'nan':
                selected_year = st.selectbox("سال مورد نظر را انتخاب کنید:", years)
                yearly_df = df_copy[df_copy['Year'] == selected_year]
                yearly_sum = pd.to_numeric(yearly_df["بالانس"], errors='coerce').sum()
                st.info(f"مجموع مقادیر بالانس برای سال *{selected_year} برابر است با: {yearly_sum:.2f}")

                with st.expander(f"مشاهده جزئیات داده‌های سال {selected_year}"):
                    st.dataframe(yearly_df.drop(columns=['Year']), use_container_width=True)
        except:
            pass

    # ==============================================================================
    # 7. فوتر نهایی (Footer)
    # ==============================================================================
    st.markdown('<div class="footer">طراحی و توسعه: مهندس هادی زندیه | شرکت فاز فیدار پارسیان</div>', unsafe_allow_html=True)

else:
    st.error("❌ خطا در بارگذاری داده‌ها. لطفاً دسترسی شیت را بررسی کنید.")
