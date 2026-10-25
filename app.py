import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- 1. تنظیمات کلی صفحه (Page Configuration) ---
st.set_page_config(
    page_title="سامانه جامع پایش وضعیت ارتعاشات", 
    layout="wide", 
    page_icon="⚙️",
    initial_sidebar_state="expanded"
)

# --- 2. استایل‌های پیشرفته CSS برای ظاهر حرفه‌ای و فارسی ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@100;400;700&display=swap');

    html, body, [class=" css"], .stMarkdown, p, h1, h2, h3, h4, h5, h6, label { 
        font-family: 'Vazirmatn', sans-serif !important; 
        direction: rtl !important; 
        text-align: right !important; 
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
        border-top: 4px solid #e74c3c; 
        z-index: 100; 
        font-size: 16px;
    }
    div[data-testid="stMetric"] {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #dee2e6;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        text-align: center;
    }
    .stDataFrame {
        border: 1px solid #dee2e6;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)
# --- 3. سیستم امنیتی ورود (Authentication) ---
def check_email_access():
    allowed_emails = [
        "vah.rezaei@gmail.com", 
        "alireza76ir@gmail.com", 
        "hamidreza.doroud@gmail.com", 
        "masoud.sa.1989823@gmail.com", 
        "tehrancement@gmail.com"
    ]
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if not st.session_state["authenticated"]:
        st.markdown("<br><br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("<div style='text-align: center;'><h2>ورود به سامانه پایش وضعیت 🧐</h2></div>", unsafe_allow_html=True)
            user_email = st.text_input("ایمیل سازمانی یا شخصی خود را وارد کنید:").strip().lower()
            if st.button("ورود به پنل مدیریت"):
                if user_email in allowed_emails:
                    st.session_state["authenticated"] = True
                    st.rerun()
                else:
                    st.error("❌ متأسفیم، ایمیل شما در لیست دسترسی‌ها نیست.")
        return False
    return True
# اجرای چک کردن دسترسی
if not check_email_access():
    st.markdown('<div class="footer">طراحی و توسعه: مهندس هادی زندیه | شرکت فاز فیدار پارسیان</div>', unsafe_allow_html=True)
    st.stop()
# --- 4. بارگذاری هوشمند داده‌ها (Data Loading) ---
# استفاده از هر دو متد برای جلوگیری از ارور 404
SHEET_URL_PUBLISH = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTI4vONsowudctVbskGkkSyQNqkkGZ8AuiykO9UKeE-8FSBZemWkR4q5DSAhpXEqwQkgsCUQy44Vvqx/pub?gid=0&single=true&output=csv"
SHEET_ID = "1H4Yf3ilu7Zhl7YZnsE6NMPOfH-Eil98_sE0_81uXns"
SHEET_URL_DIRECT = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
@st.cache_data(ttl=60)
def load_data():
    # تلاش اول: لینک Publish
    try:
        df = pd.read_csv(SHEET_URL_PUBLISH)
        df.columns = df.columns.str.strip()
        return df
    except:
        # تلاش دوم: لینک Direct Export
        try:
            df = pd.read_csv(SHEET_URL_DIRECT)
            df.columns = df.columns.str.strip()
            return df
        except Exception as e:
            st.error(f"⚠️ خطای بحرانی در اتصال به گوگل‌شیت: {e}")
            return pd.DataFrame()
df = load_data()
# --- 5. بدنه اصلی داشبورد (Main Dashboard) ---
if not df.empty:
    # --- سایدبار (Sidebar) ---
    with st.sidebar:
        st.markdown("### 🛠️ تنظیمات گزارش")
        # شناسایی ستون‌ها
        line_col = 'خط تولید' if 'خط تولید' in df.columns else df.columns[1]
        equip_col = 'عنوان تجهیز' if 'عنوان تجهیز' in df.columns else df.columns[2]
        # فیلتر خط تولید
        lines = sorted(df[line_col].dropna().unique().tolist())
        selected_line = st.selectbox("انتخاب خط تولید:", lines)
        # فیلتر تجهیز (وابسته به خط تولید)
        filtered_equips = df[df[line_col] == selected_line][equip_col].dropna().unique().tolist()
        selected_equip = st.selectbox("انتخاب تجهیز:", sorted(filtered_equips))
        st.markdown("---")
        if st.button("🔄 به‌روزرسانی لحظه‌ای داده‌ها"):
            st.cache_data.clear()
            st.rerun()
        st.info("این سامانه به صورت مستقیم با گوگل‌شیت متصل است.")
    # فیلتر کردن داده‌های نهایی
    final_df = df[(df[line_col] == selected_line) & (df[equip_col] == selected_equip)]
    # --- نمایش عنوان و شاخص‌ها (KPIs) ---
    st.title(f"📊 پایش وضعیت ارتعاشات: {selected_equip}")
    kpi1, kpi2, kpi3 = st.columns(3)
    with kpi1:
        st.metric("تعداد نقاط پایش", len(final_df))
    with kpi2:
        st.metric("خط تولید", selected_line)
    with kpi3:
        st.metric("وضعیت اتصال", "پایدار ✅")
    # --- بخش نمودارهای تحلیلی ---
    st.markdown("### 📈 تحلیل گرافیکی مقادیر")
    # شناسایی ستون‌های عددی برای رسم نمودار
    numeric_cols = final_df.select_dtypes(include=['number']).columns.tolist()
    if numeric_cols:
        # شناسایی ستون موقعیت (مثلاً P1, P2...)
        point_col = df.columns[5] if len(df.columns) > 5 else df.columns[0]
        fig = px.bar(
            final_df, 
            x=point_col, 
            y=numeric_cols, 
            barmode='group', 
            text_auto='.1f',
            color_discrete_sequence=px.colors.qualitative.Pastel,
            title=f"مقایسه ارتعاشات در نقاط مختلف برای {selected_equip}"
        )
        fig.update_layout(xaxis_title="نقاط اندازه‌گیری", yaxis_title="مقدار (mm/s)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("داده‌های عددی برای رسم نمودار یافت نشد.")
    # --- بخش جدول داده‌ها ---
    st.markdown("### 📋 جزئیات کامل داده‌ها")
    st.dataframe(final_df, use_container_width=True)
else:
    # نمایش راهنما در صورت نبود داده
    st.error("❌ متأسفانه داده‌ای از گوگل‌شیت دریافت نشد.")
    st.markdown("""
    *لطفاً موارد زیر را بررسی کنید:
    1. در گوگل‌شیت به مسیر `File` ➡️ `Share` ➡️ `Publish to web` بروید.
    2. فرمت را روی CSV قرار داده و دکمه Publish را بزنید.
    3. در بخش `Share` اصلی، دسترسی را روی Anyone with the link قرار دهید.
    """)

# --- 6. فوتر (Footer) ---
st.markdown('<div class="footer">طراحی و توسعه: مهندس هادی زندیه | شرکت فاز فیدار پارسیان</div>', unsafe_allow_html=True)
