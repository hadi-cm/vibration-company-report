import pandas as pd
import streamlit as st
import base64
# ==============================================================================
# 1. تنظیمات امنیتی
# ==============================================================================
USER_CREDENTIALS = {
    "alireza76ir@gmail.com": "siman123",
    "Vah.rezaei@gmail.com": "siman123",
    "cm.zandiyeh@gmail.com": "siman123",
    "tehrancement@gmail.com": "siman123",
    "masoud.sa.1989823@gmail.com": "siman123",
}
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if not st.session_state["authenticated"]:
        st.markdown("<h2 style='text-align: center;'>🔐 ورود به سامانه هوشمند پایش وضعیت سیمان تهران</h2>", unsafe_allow_html=True)
        with st.form("login_form"):
            email = st.text_input("ایمیل کاربری:")
            password = st.text_input("رمز عبور:", type="password")
            if st.form_submit_button("ورود به داشبورد"):
                email_lower = email.strip().lower()
                found_email = next((k for k in USER_CREDENTIALS if k.lower() == email_lower), None)
                if found_email and USER_CREDENTIALS[found_email].lower() == password.strip().lower():
                    st.session_state["authenticated"] = True
                    st.rerun()
                else:
                    st.error("❌ ایمیل یا رمز عبور اشتباه است.")
        return False
    return True
if not check_password():
    st.stop()
# ==============================================================================
# 2. تنظیمات صفحه و استایل
# ==============================================================================
st.set_page_config(page_title="داشبورد پایش وضعیت تجهیزات سیمان تهران", layout="wide")
def get_image_base64(path):
    try:
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except: return ""
logo_siman_base64 = get_image_base64("client_logo.png")
logo_faz_fidar_base64 = get_image_base64("my_logo.png")
st.markdown("""
    <style>
    .main { direction: rtl; text-align: right; }
    div[data-testid="stMetricValue"] { text-align: center; }
    .stDataFrame { direction: rtl; }
    .logo-container {
        display: flex; justify-content: space-between; align-items: center;
        margin-bottom: 20px; background-color: white; padding: 15px 30px;
        border-radius: 15px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .logo-img { width: 110px; height: auto; object-fit: contain; }
    .main-title { 
        flex: 1; text-align: center; color: #1E3A8D; 
        font-size: 26px; font-weight: bold; margin: 0 20px;
        font-family: 'Tahoma', 'Arial';
    }
    .footer {
        position: fixed; left: 0; bottom: 0; width: 100%;
        background-color: #f8f9fa; text-align: center; padding: 12px 0;
        font-weight: bold; border-top: 3px solid #2E7D32; z-index: 999;
    }
    </style>
    """, unsafe_allow_html=True)
st.markdown(f"""
    <div class="logo-container">
        <img src="data:image/png;base64,{logo_faz_fidar_base64}" class="logo-img">
        <div class="main-title">🛠️ سامانه پایش فنی و بالانس تجهیزات - سیمان تهران</div>
        <img src="data:image/png;base64,{logo_siman_base64}" class="logo-img">
    </div>
    """, unsafe_allow_html=True)
# ==============================================================================
# 3. اتصال به داده‌ها
# ==============================================================================
VIB_URL = "https://docs.google.com/spreadsheets/d/1H4Yf3ilu72hI7YZns6EXNMpOfH-EII98_sEO_81uXrs/export?format=csv&gid=0"
@st.cache_data(ttl=60)
def load_online_data():
    try:
        df = pd.read_csv(VIB_URL)
        df.columns = df.columns.str.strip()
        df = df.astype(str).apply(lambda x: x.str.strip())
        return df
    except Exception as e:
        st.error(f"❌ خطا در اتصال: {e}")
        return None
df = load_online_data()
if df is not None:
    # ==============================================================================
    # 4. بخش فیلترهای پیشرفته (جستجو و مقایسه)
    # ==============================================================================
    with st.expander("🔍 سیستم جستجو و فیلتر پیشرفته", expanded=True):
        st.write("برای مقایسه یا جستجوی سریع، از گزینه‌های زیر استفاده کنید:")
        f_col1, f_col2, f_col3 = st.columns(3)
        with f_col1:
            # فیلتر خط تولید
            all_lines = sorted([str(x) for x in df["خط تولید"].unique() if str(x) not in ['nan', 'None', '']]) if "خط تولید" in df.columns else []
            selected_line = st.selectbox("📍 انتخاب خط تولید:", ["همه"] + all_lines)
        with f_col2:
            # فیلتر واحد
            all_units = sorted([str(x) for x in df["واحد"].unique() if str(x) not in ['nan', 'None', '']]) if "واحد" in df.columns else []
            selected_unit = st.selectbox("🏢 انتخاب واحد:", ["همه"] + all_units)
        with f_col3:
            # جستجوی متنی برای نام تجهیز (جهت سرعت بیشتر در مقایسه)
            search_eq = st.text_input("🔍 جستجوی نام تجهیز یا کد:", "")
    # اعمال فیلترها روی داده‌ها
    filtered_df = df.copy()
    if selected_line != "همه":
        filtered_df = filtered_df[filtered_df["خط تولید"] == selected_line]
    if selected_unit != "همه":
        filtered_df = filtered_df[filtered_df["واحد"] == selected_unit]
    if search_eq:
        # جستجوی منعطف: اگر عبارت وارد شده در هر جای نام تجهیز بود، نمایش بده
        filtered_df = filtered_df[filtered_df["عنوان تجهیز"].str.contains(search_eq, case=False, na=False)]
    # ==============================================================================
    # 5. نمایش نتایج و متریک‌ها
    # ==============================================================================
    st.markdown("---")
    st.subheader("📈 وضعیت تحلیل فنی")
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric(label="تعداد کل تجهیزات یافت شده", value=len(filtered_df))
    with m2:
        if "بالانس" in filtered_df.columns:
            bal_done = filtered_df[~filtered_df["بالانس"].isin(['nan', 'None', ''])].shape[0]
            st.metric(label="تعداد بالانس شده", value=bal_done, delta=f"{bal_done} مورد")
        else:
            st.metric(label="ستون بالانس یافت نشد", value=0)
    with m3:
        total_cost = 0.0
        if "هزینه" in filtered_df.columns:
            cost_series = filtered_df["هزینه"].str.replace(r'[^\d.]', '', regex=True)
            total_cost = pd.to_numeric(cost_series, errors='coerce').fillna(0).sum()
            st.metric(label="جمع کل هزینه‌ها", value=f"{total_cost:,.0f} تومان")
        else:
            st.metric(label="ستون هزینه یافت نشد", value=0)
    # نمایش جدول نهایی
    st.markdown("---")
    st.subheader("📋 جدول جزئیات پایش و مقایسه")
    st.dataframe(filtered_df, use_container_width=True)
    st.markdown('<div class="footer">طراحی و توسعه: مهندس هادی زندیه | شرکت فاز فیدار پارسیان</div>', unsafe_allow_html=True)
else:
    st.error("❌ خطا در دریافت داده‌ها.")
