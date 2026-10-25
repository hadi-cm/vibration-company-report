import streamlit as st
import pandas as pd
import plotly.express as px

# --- تنظیمات صفحه ---
st.set_page_config(page_title="سامانه جامع پایش ارتعاشات", layout="wide", page_icon="⚙️")

# --- استایل CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@100;400;700&display=swap');
    html, body, [class=" css"]  { font-family: 'Vazirmatn', sans-serif; direction: rtl; text-align: right; }
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; background-color: #2c3e50; color: white; text-align: center; padding: 15px; font-weight: bold; border-top: 3px solid #e74c3c; z-index: 100; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)
# --- سیستم امنیتی ورود ---
def check_email_access():
    allowed_emails = ["vah.rezaei@gmail.com", "alireza76ir@gmail.com", "hamidreza.doroud@gmail.com", "masoud.sa.1989823@gmail.com", "tehrancement@gmail.com"]
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if not st.session_state["authenticated"]:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("<h2 style='text-align: center;'>ورود به سامانه پایش وضعیت 🧐</h2>", unsafe_allow_html=True)
            user_email = st.text_input("ایمیل خود را وارد کنید:").strip().lower()
            if st.button("ورود"):
                if user_email in allowed_emails:
                    st.session_state["authenticated"] = True
                    st.rerun()
                else:
                    st.error("ایمیل مجاز نیست.")
        return False
    return True
if not check_email_access():
    st.markdown('<div class="footer">طراحی و توسعه: مهندس هادی زندیه | شرکت فاز فیدار پارسیان</div>', unsafe_allow_html=True)
    st.stop()
# --- روش استاندارد خواندن از گوگل‌شیت (با مدیریت خطای کامل) ---
# لطفاً در گوگل‌شیت از منوی File گزینه Share و سپس Publish to web را بزنید و لینک CSV آن را اینجا قرار دهید:
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT14vONsowudctVbskGkkSyQNqkkGZ8AuiyKO9UkEe-8FSBZemWkR4q5DSAhpXEQwQkgcUQy44Vvqx/pub?gid=0&single=true&output=csv"
@st.cache_data(ttl=30)
def load_data():
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        # اگر لینک پابلیش خطا داد، از روش جایگزین با شناسه استفاده می‌کنیم
        try:
            alt_url = "https://docs.google.com/spreadsheets/d/1H4Yf3ilu7Zhl7YZnsE6NMPOfH-Eil98_sE0_81uXns/export?format=csv&gid=0"
            df = pd.read_csv(alt_url)
            df.columns = df.columns.str.strip()
            return df
        except Exception as ex:
            return pd.DataFrame()
df = load_data()
# --- نمایش داشبورد ---
if not df.empty:
    with st.sidebar:
        st.header("🛠️ فیلترهای گزارش")
        line_col = 'خط تولید' if 'خط تولید' in df.columns else df.columns[1]
        equip_col = 'عنوان تجهیز' if 'عنوان تجهیز' in df.columns else df.columns[2]
        lines = sorted(df[line_col].dropna().unique().tolist())
        selected_line = st.selectbox("انتخاب خط تولید:", lines)
        equips = sorted(df[df[line_col] == selected_line][equip_col].dropna().unique().tolist())
        selected_equip = st.selectbox("انتخاب تجهیز:", equips)
        if st.button("🔄 به‌روزرسانی داده‌ها"):
            st.cache_data.clear()
            st.rerun()
    final_df = df[(df[line_col] == selected_line) & (df[equip_col] == selected_equip)]
    st.title(f"📊 گزارش ارتعاشات: {selected_equip}")
    numeric_cols = final_df.select_dtypes(include=['number']).columns.tolist()
    if numeric_cols:
        point_col = df.columns[5] if len(df.columns) > 5 else df.columns[0]
        fig = px.bar(final_df, x=point_col, y=numeric_cols, 
                     barmode='group', title="تحلیل مقایسه‌ای نقاط اندازه‌گیری",
                     text_auto='.1f', color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(fig, use_container_width=True)
    st.subheader("📋 جزئیات داده‌های ثبت شده")
    st.dataframe(final_df, use_container_width=True)
else:
    st.error("⚠️ خطا در خواندن داده‌ها از گوگل‌شیت.")
    st.info("💡 راهنما: در گوگل‌شیت خود به مسیر File > Share > Publish to web بروید، گزینهنرم‌افزار را روی CSV بگذارید، دکمه Publish را بزنید و مطمئن شوید دسترسی فایل روی Anyone with the link است.")
st.markdown('<div class="footer">طراحی و توسعه: مهندس هادی زندیه | شرکت فاز فیدار پارسیان</div>', unsafe_allow_html=True)
