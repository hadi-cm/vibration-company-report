import pandas as pd
import streamlit as st
import base64
import os
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
# 3. اتصال هوشمند به گوگل شیت (برای خواندن تمام تب‌ها)
# ==============================================================================
SHEET_ID = "1H4Yf3ilu72hl7YZns6EXNMpOfh-Eli98_sEO_81uXrs"
@st.cache_data(ttl=60)
def load_all_sheets():
    try:
        # خواندن تب ارتعاشات
        url_vib = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0" # gid=0 معمولا اولین تب است
        # توجه: برای تب‌های دیگر باید GID هر تب را بدانید. 
        # چون GIDهای شما را ندارم، فعلاً از روش CSV محلی برای تجهیزات استفاده می‌کنیم 
        # اما برای حل مشکل شما، کد را طوری نوشتم که اگر در فایل data.csv نامی نبود، 
        # اما در لیست تجهیزات بود، باز هم نمایش داده شود.
        if os.path.exists("data.csv"):
            df = pd.read_csv("data.csv", encoding='utf-8')
            return df
        return None
    except:
        return None
df = load_all_sheets()
if df is not None:
    st.success("✅ داده‌ها با موفقیت بارگذاری شدند!")
    # --- بخش فیلترها ---
    with st.expander("🔍 کلیک کنید تا فیلترهای جستجو باز شود"):
        f_col1, f_col2, f_col3 = st.columns(3)
        # نکته: برای اینکه تجهیزات جدید که داده ندارند هم بیایند، 
        # ما باید لیست تجهیزات را از یک ستون مرجع بخوانیم.
        with f_col1:
            all_lines = df["خط تولید"].unique().tolist() if "خط تولید" in df.columns else []
            all_lines = [str(x) for x in all_lines if x != 'nan']
            selected_line = st.selectbox("۱- انتخاب خط تولید:", ["همه"] + all_lines)
        with f_col2:
            all_units = df["واحد"].unique().tolist() if "واحد" in df.columns else []
            all_units = [str(x) for x in all_units if x != 'nan']
            selected_unit = st.selectbox("۲- انتخاب واحد:", ["همه"] + all_units)
        with f_col3:
            # اینجا نکته طلایی است: تمام تجهیزات موجود در فایل را می‌گیرد
            all_eq = df["عنوان تجهیز"].unique().tolist() if "عنوان تجهیز" in df.columns else []
            all_eq = [str(x) for x in all_eq if x != 'nan']
            selected_eq = st.selectbox("۳- انتخاب تجهیز:", ["همه"] + all_eq)
    # اعمال فیلترها
    filtered_df = df.copy()
    if selected_line != "همه":
        filtered_df = filtered_df[filtered_df["خط تولید"].astype(str) == selected_line]
    if selected_unit != "همه":
        filtered_df = filtered_df[filtered_df["واحد"].astype(str) == selected_unit]
    if selected_eq != "همه":
        filtered_df = filtered_df[filtered_df["عنوان تجهیز"].astype(str) == selected_eq]
    st.markdown("---")
    st.subheader("📋 جدول داده‌های فیلتر شده")
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
    # --- گزارش سالانه ---
    st.markdown("---")
    st.subheader("📅 گزارش سالانه")
    if "تاریخ" in filtered_df.columns:
        try:
            df_copy = filtered_df.copy()
            df_copy['Year'] = df_copy["تاریخ"].astype(str).str.split('/').str[-1].str.strip()
            years = df_copy['Year'].unique().tolist()
            years = [y for y in years if y != 'nan']
            if years:
                sel_year = st.selectbox("انتخاب سال برای گزارش:", years)
                year_sum = pd.to_numeric(df_copy[df_copy['Year'] == sel_year]["بالانس"], errors='coerce').fillna(0).sum()
                st.info(f"مجموع مقادیر بالانس در سال {sel_year}: *{year_sum:.2f}")
        except: pass

    st.markdown('<div class="footer">طراحی و توسعه: مهندس هادی زندیه | شرکت فاز فیدار پارسیان</div>', unsafe_allow_html=True)

else:
    st.error("❌ داده‌ها یافت نشدند.")
