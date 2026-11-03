``python
import pandas as pd
import streamlit as st
import base64
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
        st.markdown("<h2 style='text-align: center;'>🔐 ورود به سامانه سیمان تهران</h2>", unsafe_allow_html=True)
        with st.form("login_form"):
            email = st.text_input("ایمیل:")
            password = st.text_input("رمز:", type="password")
            if st.form_submit_button("ورود"):
                email_clean = email.strip().lower()
                found_email = next((k for k in USER_CREDENTIALS if k.strip().lower() == email_clean), None)
                if found_email and USER_CREDENTIALS[found_email].strip() == password.strip():
                    st.session_state["authenticated"] = True
                    st.rerun()
                else:
                    st.error("❌ اشتباه است.")
        return False
    return True
if not check_password():
    st.stop()
st.set_page_config(page_title="داشبورد فنی", layout="wide")
def get_image_base64(path):
    try:
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except: return ""
logo_siman_base64 = get_image_base64("client_logo.png")
logo_faz_fidar_base64 = get_image_base64("my_logo.png")
st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: center; background: white; padding: 10px; border-radius: 10px;">
        <img src="data:image/png;base64,{logo_faz_fidar_base64}" width="100">
        <div style="text-align: center; color: #1E3A8D; font-weight: bold; font-size: 20px;">🛠️ سامانه پایش سیمان تهران</div>
        <img src="data:image/png;base64,{logo_siman_base64}" width="100">
    </div>
    """, unsafe_allow_html=True)
VIB_URL = "https://docs.google.com/spreadsheets/d/1H4Yf3ilu72hI7YZns6EXNMpOfH-EII98_sEO_81uXrs/export?format=csv&gid=0"
@st.cache_data(ttl=60)
def load_data():
    try:
        df = pd.read_csv(VIB_URL)
        df.columns = df.columns.str.strip()
        df = df.astype(str).apply(lambda x: x.str.strip())
        if "سیستم درایور" in df.columns:
            df = df.rename(columns={"سیستم درایور": "نوع اتصال"})
        numeric_cols = ["بالانس", "هزینه"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col].str.replace(r'[^\d.]', '', regex=True), errors='coerce').fillna(0)
        return df
    except: return None
df = load_data()
if df is not None:
    with st.expander("🔍 فیلترها", expanded=True):
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            all_lines = sorted([x for x in df["خط تولید"].unique() if x not in ['nan', 'None', '']]) if "خط تولید" in df.columns else []
            sel_line = st.selectbox("خط:", ["همه"] + all_lines)
        with c2:
            all_units = sorted([x for x in df["واحد"].unique() if x not in ['nan', 'None', '']]) if "واحد" in df.columns else []
            sel_unit = st.selectbox("واحد:", ["همه"] + all_units)
        with c3:
            search_eq = st.text_input("تجهیز:", "")
        with c4:
            date_col = next((col for col in df.columns if "تاریخ" in col), None)
            sel_date = "همه"
            if date_col:
                sel_date = st.selectbox("تاریخ:", ["همه"] + sorted(df[date_col].unique(), reverse=True))
    f_df = df.copy()
    if sel_line != "همه": f_df = f_df[f_df["خط تولید"] == sel_line]
    if sel_unit != "همه": f_df = f_df[f_df["واحد"] == sel_unit]
    if search_eq: f_df = f_df[f_df["عنوان تجهیز"].str.contains(search_eq, case=False, na=False)]
    if sel_date != "همه" and date_col: f_df = f_df[f_df[date_col] == sel_date]
    st.subheader("📈 وضعیت تحلیل")
    m1, m2, m3 = st.columns(3)
    m1.metric("تعداد رکورد", len(f_df))
    m2.metric("بالانس شده", f"{len(f_df[f_df['بالانس'] != 0]) if 'بالانس' in f_df.columns else 0}")
    m3.metric("جمع هزینه", f"{f_df['هزینه'].sum() if 'هزینه' in f_df.columns else 0:,.0f}")
    st.subheader("📋 جدول داده‌ها")
    vib_cols = [col for col in f_df.columns if any(n in str(col) for n in ["افقی", "عمودی", "محوری", "mm/s"])]
    def color_vib(val):
        try:
            n = float(str(val).replace(",", ".").replace("٫", "."))
            if n > 7.2: return 'background-color: #ffcccc; color: red'
            if n > 4.7: return 'background-color: #ffffcc; color: orange'
            return 'background-color: #e6ffed; color: green'
        except: return ''
    if vib_cols:
        st.dataframe(f_df.style.map(color_vib, subset=vib_cols), use_container_width=True, hide_index=True)
    else:
        st.dataframe(f_df, use_container_width=True, hide_index=True)
    st.markdown('<div style="text-align:center; margin-top:20px;">طراحی: مهندس هادی زندیه</div>', unsafe_allow_html=True)
else:
    st.error("خطا در دریافت داده‌ها")
