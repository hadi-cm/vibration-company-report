import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- تنظیمات صفحه ---
st.set_page_config(page_title="سامانه پایش وضعیت ارتعاشات", layout="wide", page_icon="⚙️")

# --- استایل CSS حرفه‌ای برای ظاهر فارسی و فوتر ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@100;400;700&display=swap');
    html, body, [class=" css"]  { font-family: 'Vazirmatn', sans-serif; direction: rtl; text-align: right; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
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
            st.markdown("<div style='text-align: center;'><h2>ورود به سامانه پایش وضعیت 🧐</h2></div>", unsafe_allow_html=True)
            user_email = st.text_input("ایمیل خود را وارد کنید:").strip().lower()
            if st.button("ورود"):
                if user_email in allowed_emails:
                    st.session_state["authenticated"] = True
                    st.rerun()
                else:
                    st.error("دسترسی غیرمجاز!")
        return False
    return True
if not check_email_access():
    st.markdown('<div class="footer">طراحی و توسعه: مهندس هادی زندیه | شرکت فاز فیدار پارسیان</div>', unsafe_allow_html=True)
    st.stop()
# --- بارگذاری داده‌ها با لینک Publish شده (مطمئن‌ترین روش) ---
# مهندس هادی، این لینک مستقیم و تست شده شماست:
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT14vONsowudctVbskGkkSyQNqkkGZ8AuiyKO9UkEe-8FSBZemWkR4q5DSAhpXEQwQkgcUQy44Vvqx/pub?gid=0&single=true&output=csv"
@st.cache_data(ttl=60) 
def load_data():
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = df.columns.str.strip() # پاکسازی نام ستون‌ها
        return df
    except Exception as e:
        st.error(f"⚠️ خطای دریافت داده: {e}")
        return pd.DataFrame()
df = load_data()
# --- ساختار اصلی داشبورد ---
if not df.empty:
    # --- فیلترهای سایدبار ---
    with st.sidebar:
        st.header("🛠️ فیلترهای گزارش")
        # فیلتر خط تولید
        line_col = 'خط تولید' if 'خط تولید' in df.columns else df.columns[1]
        lines = sorted(df[line_col].dropna().unique().tolist())
        selected_line = st.selectbox("انتخاب خط تولید:", lines)
        # فیلتر تجهیز
        equip_col = 'عنوان تجهیز' if 'عنوان تجهیز' in df.columns else df.columns[3]
        equip_list = sorted(df[df[line_col] == selected_line][equip_col].dropna().unique().tolist())
        selected_equip = st.selectbox("انتخاب تجهیز:", equip_list)
        st.markdown("---")
        if st.button("🔄 به‌روزرسانی داده‌ها"):
            st.cache_data.clear()
            st.rerun()
    # فیلتر کردن داده‌ها برای نمایش
    final_df = df[(df[line_col] == selected_line) & (df[equip_col] == selected_equip)]
    # --- نمایش شاخص‌ها (KPIs) ---
    st.title(f"📊 وضعیت ارتعاشات: {selected_equip}")
    kpi1, kpi2, kpi3 = st.columns(3)
    with kpi1:
        st.metric("تعداد نقاط پایش", len(final_df))
    with kpi2:
        st.metric("واحد عملیاتی", selected_line)
    with kpi3:
        st.metric("وضعیت اتصال", "برقرار ✅")
    # --- بخش نمودار (تحلیل گرافیکی) ---
    st.subheader("📈 نمودار مقایسه‌ای نقاط پایش")
    # پیدا کردن ستون‌های عددی (افقی، عمودی، محوری)
    # با توجه به تصویر شما، ستون‌های G، H، I معمولاً مقادیر هستند
    numeric_cols = final_df.select_dtypes(include=['number']).columns.tolist()
    if len(numeric_cols) >= 1:
        point_col = 'موقعیت' if 'موقعیت' in final_df.columns else final_df.columns[5]
        fig = px.bar(final_df, x=point_col, y=numeric_cols, 
                     title=f"تحلیل مقادیر ارتعاشات برای {selected_equip}",
                     barmode='group', text_auto='.1f',
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        fig.update_layout(xaxis_title="نقاط اندازه‌گیری (P1, P2...)", yaxis_title="مقدار (mm/s)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("نمودار به دلیل نبود داده عددی در این سطر نمایش داده نشد.")
    # --- نمایش جدول داده‌ها با فرمت شرطی ---
    st.subheader("📋 لیست کامل داده‌های تجهیز")
    def highlight_high_vibration(val):
        try:
            # اگر مقدار از 4.5 بیشتر بود قرمز شود
            return 'background-color: #ffcccc' if float(val) > 4.5 else ''
        except:
            return ''
    st.dataframe(final_df.style.applymap(highlight_high_vibration), use_container_width=True)
else:
    st.warning("مهندس هادی عزیز، داده‌ای یافت نشد. لطفاً مطمئن شوید در گوگل‌شیت دکمه Publish to Web فعال است.")
st.markdown('<div class="footer">طراحی و توسعه: مهندس هادی زندیه | شرکت فاز فیدار پارسیان</div>', unsafe_allow_html=True)
