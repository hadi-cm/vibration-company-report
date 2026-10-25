import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# --- تنظیمات پیشرفته صفحه ---
st.set_page_config(page_title="سامانه جامع پایش ارتعاشات", layout="wide", page_icon="⚙️")

# --- استایل CSS حرفه‌ای ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@100;400;700&display=swap');
    html, body, [class=" css"]  { font-family: 'Vazirmatn', sans-serif; direction: rtl; text-align: right; }
    .main { background-color: #f5f7f9; }
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; background-color: #2c3e50; color: white; text-align: center; padding: 15px; font-weight: bold; border-top: 3px solid #e74c3c; z-index: 100; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center; }
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
            st.markdown("<div style='text-align: center; background-color: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'><h2 style='color: #2c3e50;'>ورود به سامانه پایش وضعیت 🧐</h2></div>", unsafe_allow_html=True)
            user_email = st.text_input("ایمیل سازمانی خود را وارد کنید:").strip().lower()
            if st.button("ورود به داشبورد"):
                if user_email in allowed_emails:
                    st.session_state["authenticated"] = True
                    st.rerun()
                else:
                    st.error("دسترسی غیرمجاز! این ایمیل در لیست مجاز نیست.")
        return False
    return True
if not check_email_access():
    st.markdown('<div class="footer">طراحی و توسعه: مهندس هادی زندیه | شرکت فاز فیدار پارسیان</div>', unsafe_allow_html=True)
    st.stop()
# --- بارگذاری داده‌ها با متد بهینه ---
SHEET_ID = "1H4Yf3ilu7Zhl7YZnsE6NMPOfH-Eil98_sE0_81uXns"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
@st.cache_data(ttl=300) 
def load_data():
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = df.columns.str.strip()
        # تبدیل ستون‌های عددی برای تحلیل (اگر وجود داشته باشند)
        for col in df.columns:
            try:
                df[col] = pd.to_numeric(df[col])
            except:
                pass
        return df
    except Exception as e:
        st.error(f"⚠️ خطا در دریافت داده‌ها: {e}")
        return pd.DataFrame()
df = load_data()
if not df.empty:
    # --- سایدبار (فیلترها) ---
    with st.sidebar:
        st.markdown("## 🛠️ تنظیمات تحلیل")
        line_col = 'خط تولید' if 'خط تولید' in df.columns else df.columns[0]
        lines = sorted(df[line_col].unique().tolist())
        selected_line = st.selectbox("۱. انتخاب خط تولید", lines)
        # فیلتر دوم: انتخاب تجهیز بر اساس خط تولید
        equip_col = 'عنوان تجهیز' if 'عنوان تجهیز' in df.columns else df.columns[1]
        equip_list = sorted(df[df[line_col] == selected_line][equip_col].unique().tolist())
        selected_equip = st.selectbox("۲. انتخاب تجهیز", equip_list)
        st.markdown("---")
        st.info("داده‌ها هر ۵ دقیقه به‌روزرسانی می‌شوند.")
    # --- بدنه اصلی داشبورد ---
    st.markdown(f"## 📊 تحلیل وضعیت ارتعاشات: {selected_equip}")
    # فیلتر کردن داده‌های نهایی
    final_df = df[(df[line_col] == selected_line) & (df[equip_col] == selected_equip)]
    # --- بخش کارت‌های آماری (KPIs) ---
    col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
    with col_kpi1:
        st.metric("تعداد رکوردها", len(final_df))
    with col_kpi2:
        # فرض می‌کنیم ستونی با نام 'وضعیت' یا مشابه آن داریم
        status = "پایدار" if len(final_df) > 0 else "نامعلوم"
        st.metric("وضعیت کلی", status)
    with col_kpi3:
        st.metric("خط تولید", selected_line)
    st.markdown("### 📈 تحلیل گرافیکی مقادیر")
    # تلاش برای رسم نمودار بر اساس ستون‌های عددی
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    if numeric_cols:
        # رسم نمودار میله‌ای برای مقادیر عددی تجهیز انتخاب شده
        fig = go.Figure()
        for col in numeric_cols:
            val = final_df[col].iloc[0] if not final_df.empty else 0
            fig.add_trace(go.Bar(x=[col], y=[val], name=col))
        fig.update_layout(title=f"مقادیر ارتعاشی برای {selected_equip}", xaxis_title="پارامتر", yaxis_title="مقدار")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("ستون عددی برای رسم نمودار یافت نشد.")
    st.markdown("### 📋 جزئیات داده‌ها")
    # نمایش جدول با استایل شرطی (رنگ قرمز برای مقادیر بالای 4.5)
    def highlight_max(val):
        try:
            color = 'red' if float(val) > 4.5 else 'black'
            return f'color: {color}'
        except:
            return ''
    st.dataframe(final_df.style.applymap(highlight_max), use_container_width=True)
else:
    st.error("داده‌ای یافت نشد. لطفاً دسترسی Share گوگل شیت را بررسی کنید.")
st.markdown('<div class="footer">طراحی و توسعه: مهندس هادی زندیه | شرکت فاز فیدار پارسیان</div>', unsafe_allow_html=True)
