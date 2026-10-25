import streamlit as st
import pandas as pd
import plotly.express as px

# --- 1. تنظیمات کلی صفحه (Page Configuration) ---
st.set_page_config(
    page_title="سامانه جامع پایش ارتعاشات", 
    layout="wide", 
    page_icon="⚙️",
    initial_sidebar_state="expanded"
)

# --- 2. استایل‌های CSS برای راست‌چین و فونت فارسی ---
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
        text-align: center;
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
if not check_email_access():
    st.markdown('<div class="footer">طراحی و توسعه: مهندس هادی زندیه | شرکت فاز فیدار پارسیان</div>', unsafe_allow_html=True)
    st.stop()
# --- 4. بارگذاری هوشمند داده‌ها ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vT14vONsowudctVbskGkkSyQNqkkGZ8AuiyKO9UkEe-8FSBZemWkR4q5DSAhpXEQwQkgcUQy44Vvqx/pub?gid=0&single=true&output=csv"
@st.cache_data(ttl=60)
def load_data():
    try:
        df = pd.read_csv(SHEET_URL)
        # پاکسازی نام ستون‌ها از هرگونه فاصله اضافی
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"⚠️ خطا در دریافت داده‌ها از گوگل‌شیت: {e}")
        return pd.DataFrame()
df = load_data()
# --- 5. بدنه اصلی و فیلترهای سلسله‌مراتبی ---
if not df.empty:
    with st.sidebar:
        st.markdown("### 🛠️ تنظیمات گزارش")
        # تعریف نام دقیق ستون‌ها (مطابق با شیت شما)
        col_line = 'خط تولید'
        col_unit = 'واحد'
        col_equip = 'عنوان تجهیز'
        # بررسی وجود ستون‌ها برای جلوگیری از کرش
        available_cols = df.columns.tolist()
        if all(c in available_cols for c in [col_line, col_unit, col_equip]):
            # ۱. فیلتر خط تولید
            lines = sorted(df[col_line].dropna().unique().tolist())
            selected_line = st.selectbox("۱. انتخاب خط تولید:", lines)
            # ۲. فیلتر واحد (وابسته به خط تولید)
            units = sorted(df[df[col_line] == selected_line][col_unit].dropna().unique().tolist())
            selected_unit = st.selectbox("۲. انتخاب واحد:", units)
            # ۳. فیلتر تجهیز (وابسته به خط و واحد)
            equips = sorted(df[(df[col_line] == selected_line) & (df[col_unit] == selected_unit)][col_equip].dropna().unique().tolist())
            selected_equip = st.selectbox("۳. انتخاب تجهیز:", equips)
        else:
            st.error("❌ نام ستون‌های 'خط تولید'، 'واحد' یا 'عنوان تجهیز' در شیت یافت نشد.")
            st.stop()
        st.markdown("---")
        if st.button("🔄 به‌روزرسانی لحظه‌ای"):
            st.cache_data.clear()
            st.rerun()
    # اعمال فیلترهای نهایی
    final_df = df[(df[col_line] == selected_line) & 
                  (df[col_unit] == selected_unit) & 
                  (df[col_equip] == selected_equip)].copy()
    # --- 6. نمایش داشبورد ---
    st.title(f"📊 پایش وضعیت: {selected_equip}")
    st.markdown(f"**واحد:** {selected_unit}  |  *خط تولید:* {selected_line}")
    kpi1, kpi2 = st.columns(2)
    with kpi1:
        st.metric("تعداد نقاط پایش", len(final_df))
    with kpi2:
        st.metric("وضعیت اتصال", "پایدار ✅")
    st.markdown("### 📈 تحلیل ارتعاشات")
    # شناسایی خودکار ستون‌های عددی برای نمودار
    numeric_cols = final_df.select_dtypes(include=['number']).columns.tolist()
    if numeric_cols:
        # پیدا کردن ستون شناسنامه نقطه (اولین ستون غیرعددی یا ستون مشخص شده)
        # معمولاً ستون اول یا ستونی که نامش 'نقطه' یا 'مکان' است
        point_col = None
        for col in df.columns:
            if col not in numeric_cols and col not in [col_line, col_unit, col_equip]:
                point_col = col
                break
        if point_col is None: point_col = df.columns[0]
        fig = px.bar(
            final_df, 
            x=point_col, 
            y=numeric_cols, 
            barmode='group', 
            text_auto='.1f',
            color_discrete_sequence=px.colors.qualitative.Pastel,
            title=f"مقادیر ارتعاشات در نقاط مختلف تجهیز {selected_equip}"
        )
        fig.update_layout(xaxis_title="نقطه اندازه‌گیری", yaxis_title="مقدار (mm/s)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠️ داده عددی برای رسم نمودار یافت نشد.")
    st.markdown("### 📋 جزئیات داده‌ها")
    st.dataframe(final_df, use_container_width=True)
else:
    st.error("❌ داده‌ای دریافت نشد. لطفاً اتصال اینترنت یا لینک گوگل‌شیت را بررسی کنید.")
# --- 7. فوتر ---
st.markdown('<div class="footer">طراحی و توسعه: مهندس هادی زندیه | شرکت فاز فیدار پارسیان</div>', unsafe_allow_html=True)
