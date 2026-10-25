import streamlit as st
import pandas as pd

# --- تنظیمات صفحه ---
st.set_page_config(page_title="سامانه پایش وضعیت ارتعاشات", layout="wide", page_icon="⚙️")

# --- استایل CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@100;400;700&display=swap');
    html, body, [class=" css"]  { font-family: 'Vazirmatn', sans-serif; direction: rtl; text-align: right; }
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; background-color: #2c3e50; color: white; text-align: center; padding: 15px; font-weight: bold; border-top: 3px solid #e74c3c; z-index: 100; direction: rtl; }
    </style>
    """, unsafe_allow_html=True)
# --- تابع بررسی دسترسی ایمیل ---
def check_email_access():
    allowed_emails = ["vah.rezaei@gmail.com", "alireza76ir@gmail.com", "hamidreza.doroud@gmail.com", "masoud.sa.1989823@gmail.com", "tehrancement@gmail.com"]
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if not st.session_state["authenticated"]:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("<h2 style='text-align: center; color: #2c3e50;'>ورود به سامانه پایش وضعیت 🧐</h2>", unsafe_allow_html=True)
            user_email = st.text_input("ایمیل شما:").strip().lower()
            if st.button("بررسی دسترسی و ورود"):
                if user_email in allowed_emails:
                    st.session_state["authenticated"] = True
                    st.rerun()
                else:
                    st.error("ایمیل شما در لیست مجاز نیست.")
        return False
    return True
if not check_email_access():
    st.markdown('<div class="footer">طراحی و توسعه: مهندس هادی زندیه | شرکت فاز فیدار پارسیان</div>', unsafe_allow_html=True)
    st.stop()
# --- بارگذاری داده‌ها با شناسه دقیق استخراج شده ---
# مهندس هادی، این شناسه دقیق فایل شماست که از عکس برداشتم:
SHEET_ID = "1H4Yf3ilu7Zhl7YZnsE6NMPOH-E81_Xns" 
# استفاده از متد گوگل‌ویز برای پایداری ۱۰۰ درصدی
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=ارتعاشات"
@st.cache_data(ttl=60) 
def load_data():
    try:
        df = pd.read_csv(SHEET_URL)
        if not df.empty:
            df.columns = df.columns.str.strip()
            # تبدیل همه ستون‌ها به متن برای جلوگیری از ارورهای فرمت
            df = df.astype(str)
        return df
    except Exception as e:
        st.error(f"⚠️ خطای فنی: {e}")
        return pd.DataFrame()
df = load_data()
if not df.empty:
    with st.sidebar:
        st.markdown("### 🛠️ فیلترها")
        line_col = 'خط تولید' if 'خط تولید' in df.columns else df.columns[1]
        line_list = sorted(df[line_col].unique().tolist())
        selected_line = st.selectbox("انتخاب خط تولید", line_list)
        filtered_df = df[df[line_col] == selected_line]
    st.markdown(f"## 📊 گزارش ارتعاشات - {selected_line}")
    st.dataframe(filtered_df, use_container_width=True)
else:
    st.warning("داده‌ای یافت نشد. مهندس عزیز، لطفاً مطمئن شوید در گوگل‌شیت دکمه Share روی Anyone with the link است.")
st.markdown('<div class="footer">طراحی و توسعه: مهندس هادی زندیه | شرکت فاز فیدار پارسیان</div>', unsafe_allow_html=True)
