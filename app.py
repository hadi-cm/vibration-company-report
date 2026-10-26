import pandas as pd
import streamlit as st

# ==============================================================================
# 1. تنظیمات اولیه صفحه (Page Config)
# ==============================================================================
st.set_page_config(
    page_title="داشبورد ارتعاشات سیمان تهران - مهندس هادی زندیه", 
    layout="wide"
)

# استایل CSS برای راست‌چین کردن (RTL) و طراحی فوتر چسبان در پایین صفحه
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
    / استایل اختصاصی برای فوتر در انتهای صفحه */
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
# عنوان اصلی برنامه
st.title("📊 داشبورد جامع پایش ارتعاشات و بالانس - سیمان تهران")
st.markdown("---")
# ==============================================================================
# 2. اتصال به منبع داده (Google Sheets)
# ==============================================================================
sheet_url = "https://docs.google.com/spreadsheets/d/1H4Yf3ilu72hl7YZns6EXNMpOfh-Eli98_sEO_81uXrs/edit?gid=0#gid=0"
url_csv = sheet_url.replace("/edit?gid=", "/export?format=csv&gid=")
@st.cache_data(ttl=60)
def load_data(url):
    try:
        df = pd.read_csv(url)
        return df
    except Exception as e:
        st.error(f"خطا در اتصال به گوگل شیت: {e}")
        return None
df = load_data(url_csv)
if df is not None:
    st.success("✅ اطلاعات با موفقیت از گوگل‌شیت به‌روزرسانی شد!")
    # ==============================================================================
    # 3. بخش نمایش جدول داده‌ها
    # ==============================================================================
    st.subheader("📋 جدول جامع داده‌های ارتعاشات و بالانس")
    st.dataframe(df, use_container_width=True)
    # ==============================================================================
    # 4. بخش شاخص‌های کلیدی (Metrics)
    # ==============================================================================
    st.markdown("---")
    st.subheader("📈 شاخص‌های کلیدی")
    col1, col2 = st.columns(2)
    with col1:
        if "بالانس" in df.columns:
            balance_numeric = pd.to_numeric(df["بالانس"], errors='coerce').fillna(0)
            total_balance = balance_numeric.sum()
            st.metric(label="جمع کل بالانس‌ها (کل دوره)", value=f"{total_balance:.2f}")
        else:
            st.warning("ستون 'بالانس' در شیت یافت نشد.")
    with col2:
        if "mm/s" in df.columns:
            vibration_numeric = pd.to_numeric(df["mm/s"], errors='coerce')
            max_vibe = vibration_numeric.max()
            st.metric(label="حداکثر ارتعاش ثبت شده (mm/s)", value=f"{max_vibe:.2f}")
        else:
            st.warning("ستون 'mm/s' در شیت یافت نشد.")
    # ==============================================================================
    # 5. بخش گزارش جمع سالانه (بر اساس ستون اول: تاریخ)
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
                selected_year = st.selectbox("سال مورد نظر را انتخاب کنید تا جمع بالانس‌ها محاسبه شود:", years)
                yearly_df = df_copy[df_copy['Year'] == selected_year]
                yearly_sum = pd.to_numeric(yearly_df["بالانس"], errors='coerce').sum()
                st.info(f"مجموع مقادیر بالانس برای سال *{selected_year} برابر است با: {yearly_sum:.2f}")

                with st.expander(f"مشاهده جزئیات داده‌های سال {selected_year}"):
                    st.dataframe(yearly_df.drop(columns=['Year']), use_container_width=True)
            else:
                st.warning("سال معتبری در ستون تاریخ پیدا نشد.")

        except Exception as e:
            st.error(f"خطا در پردازش سال‌ها: {e}")
    else:
        st.error(f"ستون '{date_column}' یافت نشد.")

    # ==============================================================================
    # 6. فوتر نهایی ( Footer )
    # ==============================================================================
    # این بخش دقیقاً همان عبارتی است که خواستید و در پایین‌ترین قسمت صفحه نمایش داده می‌شود
    st.markdown('<div class="footer">طراحی و توسعه: مهندس هادی زندیه | شرکت فاز فیدار پارسیان</div>', unsafe_allow_html=True)

else:
    st.error("❌ خطا در بارگذاری داده‌ها. لطفاً دسترسی لینک گوگل شیت را بررسی کنید.")
