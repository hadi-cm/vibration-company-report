import streamlit as st
import pandas as pd

# --- تنظیمات ظاهری صفحه ---
st.set_page_config(page_title="سامانه پایش وضعیت ارتعاشات", layout="wide", page_icon="⚙️")

# --- استایل CSS برای راست‌چین کردن و فوتر ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@100;400;700&display=swap');
    html, body, [class=" css"]  { font-family: 'Vazirmatn', sans-serif; direction: rtl; text-align: right; }
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; background-color: #2c3e50; color: white; text-align: center; padding: 15px; font-weight: bold; border-top: 3px solid #e74c3c; z-index: 100; }
    </style>
    """, unsafe_allow_html=True)
# --- سیستم ورود امنیتی ---
def check_email_access():
    allowed_emails = ["vah.rezaei@gmail.com", "alireza76ir@gmail.com", "hamidreza.doroud@gmail.com", "masoud.sa.1989823@gmail.com", "tehrancement@gmail.com"]
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if not st.session_state["authenticated"]:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("<h2 style='text-align: center; color: #2c3e50;'>ورود به سامانه پایش وضعیت 🧐</h2>", unsafe_allow_html=True)
            user_email = st.text_input("ایمیل خود را وارد کنید:").strip().lower()
            if st.button("ورود به سامانه"):
                if user_email in allowed_emails:
                    st.session_state["authenticated"] = True
                    st.rerun()
                else:
                    st.error("دسترسی غیرمجاز! ایمیل شما در لیست نیست.")
        return False
    return True
if not check_email_access():
    st.markdown('<div class="footer">طراحی و توسعه: مهندس هادی زندیه | شرکت فاز فیدار پارسیان</div>', unsafe_allow_html=True)
    st.stop()
# --- بارگذاری داده‌ها (با شناسه دقیق و روش پایدار) ---
# شناسه دقیق استخراج شده از تصویر شما:
SHEET_ID = "1H4Yf3ilu7Zhl7YZnsE6NMPOfH-Eil98_sE0_81uXns"
# لینک اتصال مستقیم به تب "ارتعاشات"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=ارتعاشات"
@st.cache_data(ttl=60) 
def load_data():
    try:
        df = pd.read_csv(SHEET_URL)
        if not df.empty:
            df.columns = df.columns.str.strip() # حذف فاصله‌های احتمالی نام ستون‌ها
            df = df.astype(str) # تبدیل به متن برای نمایش بدون خطا
        return df
    except Exception as e:
        st.error(f"⚠️ خطای سیستمی در دریافت داده: {e}")
        return pd.DataFrame()
df = load_data()
# --- نمایش داشبورد ---
if not df.empty:
    with st.sidebar:
        st.markdown("### 🛠️ فیلترهای گزارش")
        # پیدا کردن ستون خط تولید
        line_col = 'خط تولید' if 'خط تولید' in df.columns else df.columns[1]
        lines = sorted(df[line_col].unique().tolist())
        selected_line = st.selectbox("انتخاب خط تولید:", lines)
        filtered_df = df[df[line_col] == selected_line]
    st.markdown(f"## 📊 گزارش وضعیت ارتعاشات - {selected_line}")
    st.dataframe(filtered_df, use_container_width=True)
else:
    st.warning("مهندس هادی عزیز، داده‌ای یافت نشد. لطفاً دسترسی Share را در گوگل‌شیت چک کنید.")
st.markdown('<div class="footer">طراحی و توسعه: مهندس هادی زندیه | شرکت فاز فیدار پارسیان</div>', unsafe_allow_html=True)
