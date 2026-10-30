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
st.set_page_config(page_title="داشبورد فنی ارتعاشات سیمان تهران", layout="wide")
st.markdown("<h2 style='text-align: center;'>سامانه پایش وضعیت تجهیزات دوار - سیمان تهران 🛠️</h2>", unsafe_allow_html=True)
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
    div[data-testid="stMetricValue"] { text-align: right; }
    .stDataFrame { direction: rtl; }
    .logo-container {
        display: flex; justify-content: space-between; align-items: center;
        margin-bottom: 20px; background-color: white; padding: 15px;
        border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .logo-img { width: 110px; height: auto; }
    </style>
    """, unsafe_allow_html=True)
st.markdown(f"""
    <div class="logo-container">
        <img src="data:image/png;base64,{logo_faz_fidar_base64}" class="logo-img">
        <h1 style='text-align: center; flex-grow: 1; color: #1E3A8D; font-size: 26px; margin: 0;'>🛠️ سامانه پایش وضعیت تجهیزات دوار - سیمان تهران</h1>
        <img src="data:image/png;base64,{logo_siman_base64}" class="logo-img">
    </div>
    """, unsafe_allow_html=True)
# ==============================================================================
# 3. اتصال به داده‌ها
# ==============================================================================
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data.csv") 
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"❌ خطا در خواندن فایل: {e}")
        return None
df = load_data()
if df is not None:
    # --- بخش فیلترها ---
    with st.expander("🔍 فیلترهای جستجو"):
        f_col1, f_col2, f_col3 = st.columns(3)
        with f_col1:
            all_lines = [x for x in df["خط تولید"].unique() if str(x) != 'nan'] if "خط تولید" in df.columns else []
            selected_line = st.selectbox("خط تولید:", ["همه"] + all_lines)
        with f_col2:
            all_units = [x for x in df["واحد"].unique() if str(x) != 'nan'] if "واحد" in df.columns else []
            selected_unit = st.selectbox("واحد:", ["همه"] + all_units)
        with f_col3:
            all_eq = [x for x in df["عنوان تجهیز"].unique() if str(x) != 'nan'] if "عنوان تجهیز" in df.columns else []
            selected_eq = st.selectbox("تجهیز:", ["همه"] + all_eq)
    # اعمال فیلترها
    filtered_df = df.copy()
    if selected_line != "همه" and "خط تولید" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["خط تولید"] == selected_line]
    if selected_unit != "همه" and "واحد" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["واحد"] == selected_unit]
    if selected_eq != "همه" and "عنوان تجهیز" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["عنوان تجهیز"] == selected_eq]
    # --- شاخص‌های کلیدی ---
    st.markdown("---")
    st.subheader("📈 وضعیت تحلیل فنی")
    m1, m2, m3 = st.columns(3)
    with m1:
        total_eq = len(filtered_df)
        st.metric(label="تعداد کل تجهیزات", value=total_eq)
    with m2:
        # منطق دینامیک: هر چه در ستون بالانس نوشته شده باشد (خالی نباشد) بشمار
        if "بالانس" in filtered_df.columns:
            bal_done = filtered_df[filtered_df["بالانس"].notna() & (filtered_df["بالانس"].astype(str).str.strip() != "")].shape[0]
            st.metric(label="تعداد بالانس شده", value=bal_done, delta=f"{bal_done} مورد")
        else:
            st.metric(label="ستون بالانس یافت نشد", value=0)
    with m3:
        # جمع کل هزینه‌ها
        total_cost = 0.0
        if "هزینه" in filtered_df.columns:
            total_cost = pd.to_numeric(filtered_df["هزینه"], errors='coerce').fillna(0).sum()
            st.metric(label="جمع کل هزینه‌ها", value=f"{total_cost:,.0f} تومان")
        else:
            st.metric(label="ستون هزینه یافت نشد", value=0)
    st.markdown("---")
    st.subheader("📋 جدول جزئیات پایش")
    st.dataframe(filtered_df, use_container_width=True)
    st.markdown("""
        <div style='text-align: center; margin-top: 50px; font-weight: bold; color: gray;'>
        طراحی و توسعه: مهندس هادی زندیه | شرکت فاز فیدار پارسیان
        </div>
        """, unsafe_allow_html=True)
else:
    st.error("❌ داده‌ها یافت نشدند. لطفاً فایل data.csv را بررسی کنید.")
