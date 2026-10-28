
```python
import pandas as pd
import streamlit as st
import base64
# ==============================================================================
# 1. تنظیمات امنیتی
# ==============================================================================
USER_CREDENTIALS = {
    "alireza76ir@gmail.com": "cement123",
    "Vah.rezaei@gmail.com": "cement123",
    "cm.zandiyeh@gmail.com": "cement123",
    "tehrancement@gmail.com": "cement123",
    "masoud.sa.1989823@gmail.com": "cement123",
    "hamidrezadorod@gmail.com": "cement38p02146",
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
st.set_page_config(page_title="داشبورد ارتعاشات سیمان تهران", layout="wide")
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
    .footer {
        position: fixed; left: 0; bottom: 0; width: 100%;
        background-color: #f8f9fa; text-align: center; padding: 12px 0;
        font-weight: bold; border-top: 3px solid #2E7D32; z-index: 999;
    }
    .error-box {
        background-color: #f8d7da; color: #721c24; padding: 15px;
        border-radius: 5px; border: 1px solid #f5c6cb; margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)
st.markdown(f"""
    <div class="logo-container">
        <img src="data:image/png;base64,{logo_faz_fidar_base64}" class="logo-img">
        <h1 style='text-align: center; flex-grow: 1; color: #1E3A8D; font-size: 26px; margin: 0;'>📊 داشبورد جامع پایش ارتعاشات و بالانس - سیمان تهران</h1>
        <img src="data:image/png;base64,{logo_siman_base64}" class="logo-img">
    </div>
    """, unsafe_allow_html=True)
# ==============================================================================
# 3. اتصال هوشمند به گوگل‌شیت (رفع خطای 404)
# ==============================================================================
SHEET_ID = "1H4Yf3ilu72hl7YZns6EXNMpOfh-Eli98_sEO_81uXrs"
# لینک خروجی مستقیم برای تب ارتعاشات (gid=0 معمولا تب اول است)
VIB_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
@st.cache_data(ttl=60)
def load_online_data():
    try:
        # استفاده از pandas برای خواندن مستقیم CSV
        df = pd.read_csv(VIB_URL)
        # پاک‌سازی نام ستون‌ها از هرگونه فاصله اضافی
        df.columns = df.columns.str.strip()
        # پاک‌سازی داده‌ها
        for col in df.columns:
            df[col] = df[col].astype(str).str.strip()
        return df
    except Exception as e:
        st.error(f"❌ خطا در اتصال به گوگل‌شیت: {e}")
        return None
df = load_online_data()
if df is not None:
    # --- سیستم شناسایی نام‌های اشتباه (برای جلوگیری از خرابی ترندها) ---
    if "عنوان تجهیز" in df.columns:
        name_counts = df["عنوان تجهیز"].value_counts()
        # نام‌هایی که فقط یک بار تکرار شده‌اند مشکوک به غلط تایپی هستند
        suspicious_names = name_counts[name_counts == 1].index.tolist()
        # حذف مقادیر nan از لیست مشکوک‌ها
        suspicious_names = [n for n in suspicious_names if n != 'nan' and n != '']
        if len(suspicious_names) > 0:
            st.markdown(f"""<div class="error-box">🛑 <b>هشدار تطبیق نام تجهیزات:</b><br>
            تعداد {len(suspicious_names)} مورد نام تجهیز شناسایی شد که احتمالاً غلط تایپی دارند.<br>
            <b>موارد مشکوک:</b> {", ".join(suspicious_names)}</div>""", unsafe_allow_html=True)
    # --- بخش فیلترها ---
    with st.expander("🔍 فیلترهای جستجو"):
        f_col1, f_col2, f_col3 = st.columns(3)
        with f_col1:
            all_lines = [x for x in df["خط تولید"].unique() if x != 'nan'] if "خط تولید" in df.columns else []
            selected_line = st.selectbox("۱- خط تولید:", ["همه"] + all_lines)
        with f_col2:
            all_units = [x for x in df["واحد"].unique() if x != 'nan'] if "واحد" in df.columns else []
            selected_unit = st.selectbox("۲- واحد:", ["همه"] + all_units)
        with f_col3:
            all_eq = [x for x in df["عنوان تجهیز"].unique() if x != 'nan'] if "عنوان تجهیز" in df.columns else []
            selected_eq = st.selectbox("۳- تجهیز:", ["همه"] + all_eq)
    # اعمال فیلترها
    filtered_df = df.copy()
    if selected_line != "همه" and "خط تولید" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["خط تولید"] == selected_line]
    if selected_unit != "همه" and "واحد" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["واحد"] == selected_unit]
    if selected_eq != "همه" and "عنوان تجهیز" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["عنوان تجهیز"] == selected_eq]
    st.markdown("---")
    st.subheader("📋 جدول داده‌ها")
    st.dataframe(filtered_df, use_container_width=True)
    # --- شاخص‌های کلیدی ---
    st.markdown("---")
    st.subheader("📈 شاخص‌های کلیدی")
    m1, m2 = st.columns(2)
    with m1:
        val_balance = 0.0
        if "بالانس" in filtered_df.columns:
            val_balance = pd.to_numeric(filtered_df["بالانس"], errors='coerce').fillna(0).sum()
        st.metric(label="جمع کل بالانس‌ها", value=f"{val_balance:.2f}")
    with m2:
        val_vib = 0.0
        if "mm/s" in filtered_df.columns:
            val_vib = pd.to_numeric(filtered_df["mm/s"], errors='coerce').fillna(0).max()
        st.metric(label="حداکثر ارتعاش (mm/s)", value=f"{val_vib:.2f}")
    st.markdown('<div class="footer">طراحی و توسعه: مهندس هادی زندیه | شرکت فاز فیدار پارسیان</div>', unsafe_allow_html=True)
else:
    st.error("❌ داده‌ها یافت نشدند. لطفاً تنظیمات Share گوگل‌شیت را بررسی کنید.")
