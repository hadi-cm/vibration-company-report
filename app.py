import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- تنظیمات صفحه ---
st.set_page_config(page_title="سامانه پایش وضعیت ارتعاشات", layout="wide", page_icon="⚙️")

# --- استایل CSS برای راست‌چین کردن، فونت و طراحی فوتر ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@100;400;700&display=swap');
    html, body, [class=" css"]  {
        font-family: 'Vazirmatn', sans-serif;
        direction: rtl;
        text-align: right;
    }
    .stSelectbox label, .stMarkdown p {
        direction: rtl;
        text-align: right;
    }
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #2c3e50;
        color: white;
        text-align: center;
        padding: 15px;
        font-weight: bold;
        font-size: 16px;
        border-top: 3px solid #e74c3c;
        z-index: 100;
        direction: rtl;
    }
    .footer span {
        margin: 0 15px;
    }
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
# --- اجرای بررسی دسترسی ---
if not check_email_access():
    st.markdown('<div class="footer"><span>طراحی و توسعه: مهندس هادی زندیه</span> | <span>شرکت فاز فیدار پارسیان</span></div>', unsafe_allow_html=True)
    st.stop()
# --- بارگذاری داده‌ها (نسخه جدید و ضد خطا) ---
# شناسه شیت شماست
SHEET_ID = "1H4YlzU7ZNH27YNzE6NMPOH-E81_Xns"
# لینک مستقیم برای دانلود به صورت CSV (پایدارترین حالت)
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
@st.cache_data(ttl=600) 
def load_data():
    try:
        # خواندن مستقیم از لینک اکسپورت گوگل
        df = pd.read_csv(SHEET_URL)
        if not df.empty:
            df['عنوان تجهیز'] = df['عنوان تجهیز'].astype(str)
            df = df.dropna(subset=['عنوان تجهیز'])
        return df
    except Exception as e:
        st.error(f"⚠️ خطا در اتصال به داده‌ها: {e}")
        return pd.DataFrame()
df = load_data()
if not df.empty:
    # --- منوی سمت راست (Sidebar) ---
    with st.sidebar:
        st.markdown("### 🛠️ فیلترهای جستجو")
        section = st.selectbox("انتخاب بخش", ["تحلیل مقایسه‌ای تجهیزات", "تحلیل تاریخچه ارتعاشات"])
        if section == "تحلیل تاریخچه ارتعاشات":
            production_lines = sorted(df['خط تولید'].unique().tolist())
            selected_line = st.selectbox("انتخاب خط تولید", production_lines)
            units_in_line = sorted(df[df['خط تولید'] == selected_line]['واحد'].unique().tolist())
            selected_unit = st.selectbox("انتخاب واحد", units_in_line)
            filtered_equipment = sorted(df[(df['خط تولید'] == selected_line) & (df['واحد'] == selected_unit)]['عنوان تجهیز'].unique().tolist())
            selected_equipment = st.selectbox("انتخاب تجهیز", filtered_equipment)
            final_df = df[(df['خط تولید'] == selected_line) & (df['واحد'] == selected_unit) & (df['عنوان تجهیز'] == selected_equipment)]
        else:
            all_equipment = sorted(df['عنوان تجهیز'].unique().tolist())
            selected_equipment = st.selectbox("انتخاب تجهیز", all_equipment)
            final_df = df[df['عنوان تجهیز'] == selected_equipment]
    # --- بدنه اصلی برنامه ---
    st.markdown(f"## 🔍 تحلیل {section} - {selected_equipment}")
    if not final_df.empty:
        st.write("### 📊 داده‌های استخراج شده")
        st.dataframe(final_df, use_container_width=True)
    else:
        st.warning("داده‌ای برای این تجهیز یافت نشد.")
    st.markdown('<div class="footer"><span>طراحی و توسعه: مهندس هادی زندیه</span> | <span>شرکت فاز فیدار پارسیان</span></div>', unsafe_allow_html=True)
else:
    st.error("داده‌ای از گوگل شیت دریافت نشد. لطفاً دسترسی Share را روی Anyone with the link قرار دهید.")
    st.markdown('<div class="footer"><span>طراحی و توسعه: مهندس هادی زندیه</span> | <span>شرکت فاز فیدار پارسیان</span></div>', unsafe_allow_html=True)
