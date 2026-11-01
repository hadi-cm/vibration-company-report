import pandas as pd
import streamlit as st
import base64
# ==============================================================================
# 1. تنظیمات امنیتی
# ==============================================================================
USER_CREDENTIALS = {
    "alireza76ir@gmail.com": "siman123",
    "vah.rezaei@gmail.com": "siman123",
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
                email_clean = email.strip().lower()
                found_email = next((k for k in USER_CREDENTIALS if k.strip().lower() == email_clean), None)
                if found_email and USER_CREDENTIALS[found_email].strip() == password.strip():
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
    div[data-testid="stMetricValue"] { text-align: center; }
    .logo-container {
        display: flex; justify-content: space-between; align-items: center;
        margin-bottom: 20px; background-color: white; padding: 15px 30px;
        border-radius: 15px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .logo-img { width: 110px; height: auto; object-fit: contain; }
    .main-title { 
        flex: 1; text-align: center; color: #1E3A8D; 
        font-size: 26px; font-weight: bold; margin: 0 20px;
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
        <div class="main-title">🛠️ سامانه پایش وضعیت تجهیزات سیمان تهران</div>
        <img src="data:image/png;base64,{logo_siman_base64}" class="logo-img">
    </div>
    """, unsafe_allow_html=True)
# ==============================================================================
# 3. بارگذاری داده‌ها با متد شماره ستون (ضد به‌هم‌ریختگی نام‌ها)
# ==============================================================================
VIB_URL = "https://docs.google.com/spreadsheets/d/1H4Yf3ilu72hI7YZns6EXNMpOfH-EII98_sEO_81uXrs/export?format=csv&gid=0"
@st.cache_data(ttl=60)
def load_and_process_data():
    try:
        # خواندن فایل بدون در نظر گرفتن نام ستون‌ها در ابتدا
        df = pd.read_csv(VIB_URL)
        # تعریف دستی نام ستون‌ها بر اساس ترتیب عکس شما
        # این کار باعث می‌شود دیگر مهم نباشد نام‌ها در اکسل به‌هم‌ریخته‌اند یا نه
        manual_columns = [
            "تاریخ", "تعداد", "خط تولید", "واحد", "عنوان تجهیز", "محل اندازه گیری", 
            "v1", "v2", "v3", "v_max", "mm/s", "تجهیز", "نوع اتصال", "دما", 
            "توضیحات", "وضعیت", "بالانس", "شماره بیرینگ", "هزینه", "اولویت"
        ]
        # اگر تعداد ستون‌های فایل با لیست ما یکی نبود، نام‌ها را به صورت پیش‌فرض می‌گذاریم
        if len(df.columns) != len(manual_columns):
            # اگر تعداد متفاوت بود، فقط نام‌های اصلی را جایگزین می‌کنیم
            df.columns = [f"Col_{i}" for i in range(len(df.columns))]
            # تلاش برای یافتن ستون mm/s در میان نام‌های به‌هم‌ریخته
            for i, col in enumerate(df.columns):
                if "mm/s" in str(df.columns[i]):
                    df.rename(columns={df.columns[i]: "mm/s"}, inplace=True)
        else:
            df.columns = manual_columns
        # تبدیل ستون ارتعاش به عدد
        if "mm/s" in df.columns:
            df["mm/s"] = pd.to_numeric(df["mm/s"].astype(str).str.replace(r'[^\d.]', '', regex=True), errors='coerce').fillna(0.0)
        # تبدیل هزینه به عدد
        if "هزینه" in df.columns:
            df["هزینه"] = pd.to_numeric(df["هزینه"].astype(str).str.replace(r'[^\d.]', '', regex=True), errors='coerce').fillna(0.0)
        return df
    except Exception as e:
        st.error(f"❌ خطا در پردازش داده‌ها: {e}")
        return None
df = load_and_process_data()
if df is not None:
    # ==============================================================================
    # 4. فیلترها
    # ==============================================================================
    with st.expander("🔍 سیستم جستجو و فیلتر پیشرفته", expanded=True):
        f_row1_col1, f_row1_col2, f_row1_col3 = st.columns(3)
        with f_row1_col1:
            all_lines = sorted([str(x) for x in df["خط تولید"].unique() if str(x) not in ['nan', 'None', '']]) if "خط تولید" in df.columns else []
            selected_line = st.selectbox("📍 خط تولید:", ["همه"] + all_lines)
        with f_row1_col2:
            all_units = sorted([str(x) for x in df["واحد"].unique() if str(x) not in ['nan', 'None', '']]) if "واحد" in df.columns else []
            selected_unit = st.selectbox("🏢 واحد:", ["همه"] + all_units)
        with f_row1_col3:
            search_eq = st.text_input("🔍 نام تجهیز:", "")
        f_row2_col1, f_row2_col2 = st.columns(2)
        with f_row2_col1:
            if "محل اندازه گیری" in df.columns:
                all_points = sorted([str(x).strip().upper() for x in df["محل اندازه گیری"].unique() if str(x) not in ['nan', 'None', '']])
                selected_point = st.selectbox("📍 نقطه اندازه‌گیری (P):", ["همه نقاط"] + all_points)
            else:
                selected_point = "همه نقاط"
        with f_row2_col2:
            if "تاریخ" in df.columns:
                available_dates = sorted(df["تاریخ"].unique(), reverse=True)
                selected_date = st.selectbox("📅 تاریخ خاص:", ["همه تاریخ‌ها"] + list(available_dates))
            else:
                selected_date = "همه تاریخ‌ها"
    # اعمال فیلترها
    filtered_df = df.copy()
    if selected_line != "همه" and "خط تولید" in df.columns: filtered_df = filtered_df[filtered_df["خط تولید"] == selected_line]
    if selected_unit != "همه" and "واحد" in df.columns: filtered_df = filtered_df[filtered_df["واحد"] == selected_unit]
    if search_eq and "عنوان تجهیز" in df.columns: filtered_df = filtered_df[filtered_df["عنوان تجهیز"].str.contains(search_eq, case=False, na=False)]
    if selected_point != "همه نقاط" and "محل اندازه گیری" in df.columns: 
        filtered_df = filtered_df[filtered_df["محل اندازه گیری"].astype(str).str.strip().str.upper() == selected_point]
    if selected_date != "همه تاریخ‌ها" and "تاریخ" in df.columns:
        filtered_df = filtered_df[filtered_df["تاریخ"] == selected_date]
    # ==============================================================================
    # 5. متریک‌ها
    # ==============================================================================
    st.markdown("---")
    st.subheader("📈 وضعیت تحلیل فنی")
    m1, m2, m3 = st.columns(3)
    with m1: st.metric("تعداد رکوردها", len(filtered_df))
    with m2:
        bal_count = filtered_df[~filtered_df["بالانس"].isin(['nan', 'None', ''])].shape[0] if "بالانس" in filtered_df.columns else 0
        st.metric("تعداد بالانس شده", bal_count)
    with m3:
        total_cost = filtered_df["هزینه"].sum() if "هزینه" in filtered_df.columns else 0.0
        st.metric("جمع هزینه‌ها", f"{total_cost:,.0f} تومان")
    # ==============================================================================
    # 6. نمایش جدول با رنگ‌بندی
    # ==============================================================================
    st.markdown("---")
    st.subheader("📋 جدول جزئیات پایش و مقایسه")
    def apply_color(val):
        try:
            num = float(val)
            if num > 7.2: return 'background-color: #ff4b4b; color: white; font-weight: bold'
            if num > 4.7: return 'background-color: #ffff00; color: black; font-weight: bold'
            return '' 
        except: return ''
    if "mm/s" in filtered_df.columns and not filtered_df.empty:
        styled_df = filtered_df.style.map(apply_color, subset=["mm/s"])
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
        st.info(f"💡 راهنمای رنگی ستون mm/s: سفید (عادی) | زرد (۴.۷-۷.۲) | قرمز (بالای ۷.۲)")
    else:
        st.dataframe(filtered_df, use_container_width=True, hide_index=True)
    st.markdown('<div class="footer">طراحی و توسعه: مهندس هادی زندیه | شرکت فاز فیدار پارسیان</div>', unsafe_allow_html=True)
else:
    st.error("❌ خطا در دریافت داده‌ها. لطفاً دسترسی گوگل‌شیت را بررسی کنید.")
