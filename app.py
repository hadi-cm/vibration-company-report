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
    .logo-container {
        display: flex; justify-content: space-between; align-items: center;
        margin-bottom: 20px; background-color: white; padding: 15px 30px;
        border-radius: 15px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .logo-img { width: 110px; height: auto; object-fit: contain; }
    .main-title { flex: 1; text-align: center; color: #1E3A8D; font-size: 26px; font-weight: bold; }
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; background-color: #f8f9fa; text-align: center; padding: 12px 0; font-weight: bold; border-top: 3px solid #2E7D32; z-index: 999; }
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
# 3. بارگذاری داده‌ها
# ==============================================================================
VIB_URL = "https://docs.google.com/spreadsheets/d/1H4Yf3ilu72hI7YZns6EXNMpOfH-EII98_sEO_81uXrs/export?format=csv&gid=0"
@st.cache_data(ttl=60)
def load_data():
    try:
        df = pd.read_csv(VIB_URL)
        # نام‌گذاری بر اساس لیست شما
        expected_cols = [
            "تاریخ", "خط تولید", "واحد", "عنوان تجهیز", "تصویر", "محل اندازه گیری", 
            "عمودی", "افقی", "محوری", "mm/s", "دور", "بالانس", "سیستم درایور", 
            "دما", "تناژ", "توضیحات", "وضعیت", "شماره بیرینگ", "اقدام اصلاحی", "هزینه", "اولویت"
        ]
        if len(df.columns) == len(expected_cols):
            df.columns = expected_cols
        else:
            # اگر تعداد ستون‌ها متفاوت بود، از نام‌های اصلی استفاده می‌کنیم
            for i, col in enumerate(df.columns):
                col_str = str(col).lower()
                if 'mm/s' in col_str: df.rename(columns={col: 'mm/s'}, inplace=True)
                if 'تاریخ' in col_str: df.rename(columns={col: 'تاریخ'}, inplace=True)
                if 'وضعیت' in col_str: df.rename(columns={col: 'وضعیت'}, inplace=True)
                if 'عنوان تجهیز' in col_str: df.rename(columns={col: 'عنوان تجهیز'}, inplace=True)
                if 'محل' in col_str: df.rename(columns={col: 'محل اندازه گیری'}, inplace=True)
        for col in ['mm/s', 'هزینه', 'عمودی', 'افقی', 'محوری']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col].astype(str).str.replace(r'[^\d.]', '', regex=True), errors='coerce').fillna(0.0)
        return df
    except Exception as e:
        st.error(f"❌ خطا در بارگذاری: {e}")
        return None
df = load_data()
if df is not None:
    # ==============================================================================
    # 4. فیلترها
    # ==============================================================================
    with st.expander("🔍 سیستم جستجو و فیلتر پیشرفته", expanded=True):
        f1, f2, f3 = st.columns(3)
        with f1:
            line_list = ["همه"] + sorted(df["خط تولید"].unique().tolist())
            sel_line = st.selectbox("📍 خط تولید:", line_list)
        with f2:
            unit_list = ["همه"] + sorted(df["واحد"].unique().tolist())
            sel_unit = st.selectbox("🏢 واحد:", unit_list)
        with f3:
            search_eq = st.text_input("🔍 جستجوی نام تجهیز:", "")
        f4, f5 = st.columns(2)
        with f4:
            point_list = ["همه نقاط"] + sorted(df["محل اندازه گیری"].unique().tolist())
            sel_point = st.selectbox("📍 نقطه اندازه‌گیری:", point_list)
        with f5:
            date_list = ["همه تاریخ‌ها"] + sorted(df["تاریخ"].unique().tolist(), reverse=True)
            sel_date = st.selectbox("📅 تاریخ خاص:", date_list)
    f_df = df.copy()
    if sel_line != "همه": f_df = f_df[f_df["خط تولید"] == sel_line]
    if sel_unit != "همه": f_df = f_df[f_df["واحد"] == sel_unit]
    if search_eq: f_df = f_df[f_df["عنوان تجهیز"].str.contains(search_eq, case=False, na=False)]
    if sel_point != "همه نقاط": f_df = f_df[f_df["محل اندازه گیری"] == sel_point]
    if sel_date != "همه تاریخ‌ها": f_df = f_df[f_df["تاریخ"] == sel_date]
    # ==============================================================================
    # 5. متریک‌ها
    # ==============================================================================
    st.subheader("📈 وضعیت تحلیل فنی")
    m1, m2, m3 = st.columns(3)
    with m1: st.metric("تعداد رکوردها", len(f_df))
    with m2:
        bal_cnt = f_df[f_df["بالانس"].astype(str).str.contains('نیاز', na=False)].shape[0]
        st.metric("نیاز به بالانس", bal_cnt)
    with m3:
        total_c = f_df["هزینه"].sum()
        st.metric("جمع هزینه‌ها", f"{total_c:,.0f} تومان")
    # ==============================================================================
    # 6. نمودار ترند (Trend Analysis) - بدون نیاز به Plotly
    # ==============================================================================
    if not f_df.empty and search_eq:
        st.markdown("---")
        st.subheader("📉 تحلیل روند ارتعاش (Trend)")
        trend_df = df[df["عنوان تجهیز"].str.contains(search_eq, case=False, na=False)].copy()
        if not trend_df.empty:
            trend_df = trend_df.sort_values("تاریخ")
            # استفاده از نمودار داخلی استریم‌لیت (Line Chart)
            st.line_chart(trend_df.set_index("تاریخ")["mm/s"])
            st.caption("💡 برای مشاهده نمودار، حتماً نام تجهیز را در فیلتر جستجو تایپ کنید.")
        else:
            st.warning("تجهیزی با این نام یافت نشد.")
    # ==============================================================================
    # 7. نمایش جدول و رنگ‌بندی
    # ==============================================================================
    st.markdown("---")
    st.subheader("📋 جدول جزئیات پایش و مقایسه")
    def color_cells(row):
        styles = ['']  len(row)
        # رنگ‌بندی mm/s
        if 'mm/s' in row.index:
            val = row['mm/s']
            idx = row.index.get_loc('mm/s')
            if val > 11: styles[idx] = 'background-color: #ff4b4b; color: white; font-weight: bold'
            elif val > 7.2: styles[idx] = 'background-color: #ffa500; color: black; font-weight: bold'
            elif val > 4.7: styles[idx] = 'background-color: #ffff00; color: black; font-weight: bold'
            else: styles[idx] = 'background-color: #ffffff; color: black'

        # رنگ‌بندی وضعیت
        if 'وضعیت' in row.index:
            stat = str(row['وضعیت']).strip()
            idx = row.index.get_loc('وضعیت')
            if 'هشدار' in stat: styles[idx] = 'background-color: #ff4b4b; color: white; font-weight: bold'
            elif 'مراقبت' in stat: styles[idx] = 'background-color: #ffff00; color: black; font-weight: bold'
            elif 'نرمال' in stat: styles[idx] = 'background-color: #ffffff; color: black'
        return styles

    if not f_df.empty:
        st.dataframe(f_df.style.apply(color_cells, axis=1), use_container_width=True, hide_index=True)
    else:
        st.warning("هیچ داده‌ای با این فیلترها پیدا نشد.")

    st.markdown('<div class="footer">طراحی و توسعه: مهندس هادی زندیه | شرکت فاز فیدار پارسیان</div>', unsafe_allow_html=True)

else:
    st.error("❌ خطا در دریافت داده‌ها.")
