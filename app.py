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
        <h1 style='text-align: center; flex-grow: 1; color: #1E3A8D; font-size: 26px; margin: 0;'>🛠️ سامانه پایش فنی و بالانس تجهیزات - سیمان تهران</h1>
        <img src="data:image/png;base64,{logo_siman_base64}" class="logo-img">
    </div>
    """, unsafe_allow_html=True)
# ==============================================================================
# 3. اتصال به گوگل‌شیت
# ==============================================================================
SHEET_ID = "1H4Yf3ilu72hl7YZns6EXNMpOfh-Eli98_sEO_81uXrs"
VIB_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
@st.cache_data(ttl=60)
def load_online_data():
    try:
        df = pd.read_csv(VIB_URL)
        df.columns = df.columns.str.strip()
        # تبدیل تمام مقادیر به رشته برای جلوگیری از خطای nan
        df = df.astype(str).apply(lambda x: x.str.strip())
        return df
    except Exception as e:
        st.error(f"❌ خطا در اتصال به گوگل‌شیت: {e}")
        return None
df = load_online_data()
if df is not None:
    # --- بخش فیلترها ---
    with st.expander("🔍 فیلترهای جستجو"):
        f_col1, f_col2, f_col3 = st.columns(3)
        with f_col1:
            all_lines = sorted([x for x in df["خط تولید"].unique() if x not in ['nan', 'None', '']]) if "خط تولید" in df.columns else []
            selected_line = st.selectbox("۱- خط تولید:", ["همه"] + all_lines)
        with f_col2:
            all_units = sorted([x for x in df["واحد"].unique() if x not in ['nan', 'None', '']]) if "واحد" in df.columns else []
            selected_unit = st.selectbox("۲- واحد:", ["همه"] + all_units)
        with f_col3:
            all_eq = sorted([x for x in df["عنوان تجهیز"].unique() if x not in ['nan', 'None', '']]) if "عنوان تجهیز" in df.columns else []
            selected_eq = st.selectbox("۳- تجهیز:", ["همه"] + all_eq)
    # اعمال فیلترها
    filtered_df = df.copy()
    if selected_line != "همه":
        filtered_df = filtered_df[filtered_df["خط تولید"] == selected_line]
    if selected_unit != "همه":
        filtered_df = filtered_df[filtered_df["واحد"] == selected_unit]
    if selected_eq != "همه":
        filtered_df = filtered_df[filtered_df["عنوان تجهیز"] == selected_eq]
    # --- شاخص‌های کلیدی ---
    st.markdown("---")
    st.subheader("📈 وضعیت تحلیل فنی")
    m1, m2, m3 = st.columns(3)
    with m1:
        total_eq = len(filtered_df)
        st.metric(label="تعداد کل تجهیزات", value=total_eq)
    with m2:
        # اصلاح شمارش بالانس: فقط مواردی که nan یا None یا خالی نیستند
        if "بالانس" in filtered_df.columns:
            bal_done = filtered_df[~filtered_df["بالانس"].isin(['nan', 'None', ''])].shape[0]
            st.metric(label="تعداد بالانس شده", value=bal_done, delta=f"{bal_done} مورد")
        else:
            st.metric(label="ستون بالانس یافت نشد", value=0)
    with m3:
        total_cost = 0.0
        if "هزینه" in filtered_df.columns:
            # تبدیل ستون هزینه به عدد (حذف کاما و کاراکترهای غیر عددی)
            costs = filtered_df["هزینه"].str.replace(',', '').replace('nan', '0')
            total_cost = pd.to_numeric(costs, errors='coerce').fillna(0).sum()
            st.metric(label="جمع کل هزینه‌ها", value=f"{total_cost:,.0f} تومان")
        else:
            st.metric(label="ستون هزینه یافت نشد", value=0)
    # --- بخش نمودار روند ارتعاشات (اگر تجهیز خاصی انتخاب شده باشد) ---
    if selected_eq != "همه":
        st.markdown("---")
        st.subheader(f"📉 روند ارتعاشات تجهیز: {selected_eq}")
        # فرض بر این است که ستونی به نام 'تاریخ' و 'مقدار ارتعاش' دارید
        # در اینجا من از ستون‌هایی که احتمالا دارید استفاده می‌کنم، اگر نامشان متفاوت است تغییر دهید
        date_col = next((col for col in df.columns if "تاریخ" in col), None)
        val_col = next((col for col in df.columns if "mm/s" in col or "مقدار" in col), None)
        if date_col and val_col:
            trend_df = filtered_df[[date_col, val_col]].copy()
            trend_df[val_col] = pd.to_numeric(trend_df[val_col], errors='coerce')
            trend_df = trend_df.dropna().sort_values(by=date_col)
            st.line_chart(data=trend_df, x=date_col, y=val_col)
        else:
            st.info("برای نمایش نمودار، ستون‌های 'تاریخ' و 'مقدار ارتعاش' در شیت مورد نیاز است.")
    # --- جدول جزئیات ---
    st.markdown("---")
    st.subheader("📋 جدول جزئیات پایش")
    st.dataframe(filtered_df, use_container_width=True)
    st.markdown('<div class="footer">طراحی و توسعه: مهندس هادی زندیه | شرکت فاز فیدار پارسیان</div>', unsafe_allow_html=True)
else:
    st.error("❌ خطا در دریافت داده‌ها از گوگل‌شیت. لطفاً دسترسی فایل را بررسی کنید.")
