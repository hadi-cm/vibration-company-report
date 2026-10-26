import pandas as pd
import streamlit as st
import base64

# ==============================================================================
# 1. تنظیمات امنیتی و دسترسی (ایمیل‌ها و پسوردهای مجاز)
# ==============================================================================
# هر ایمیل و پسوردی که در این لیست باشد، اجازه ورود دارد
USER_CREDENTIALS = {
    "alireza76ir@gmail.com": "Siman123",
    "Vah.rezaei@gmail.com": "Siman123",
    "cm.zandiyeh@gmail.com": "Siman123",
    "tehrancement@gmail.com": "Siman123",
    "masoud.sa.1989823@gmail.com": "Siman123",
}

def check_password():
    """توابع مربوط به احراز هویت کاربر"""
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        st.markdown("<h2 style='text-align: center;'>🔐 ورود به سامانه پایش ارتعاشات</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>لطفاً ایمیل و رمز عبور خود را وارد نمایید</p>", unsafe_allow_html=True)

        with st.form("login_form"):
            email = st.text_input("ایمیل کاربری:")
            password = st.text_input("رمز عبور:", type="password")
            submit_button = st.form_submit_button("ورود به داشبورد")

            if submit_button:
                # تبدیل ایمیل ورودی به حروف کوچک برای جلوگیری از خطای تایپی
                email_lower = email.strip().lower()
                # پیدا کردن ایمیل در لیست (با نادیده گرفتن حروف بزرگ و کوچک)
                found_email = next((k for k in USER_CREDENTIALS if k.lower() == email_lower), None)

                if found_email and USER_CREDENTIALS[found_email] == password:
                    st.session_state["authenticated"] = True
                    st.rerun()
                else:
                    st.error("❌ ایمیل یا رمز عبور اشتباه است. لطفاً دوباره تلاش کنید.")
        return False
    return True

# اجرای بررسی دسترسی در ابتدای برنامه
if not check_password():
    st.stop()

# ==============================================================================
# 2. تنظیمات اولیه صفحه (Page Config)
# ==============================================================================
st.set_page_config(
    page_title="داشبورد ارتعاشات سیمان تهران - مهندس هادی زندیه", 
    layout="wide"
)

# تابع برای خواندن عکس‌های محلی
def get_image_base64(path):
    try:
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except:
        return ""

logo_siman_base64 = get_image_base64("client_logo.png")
logo_faz_fidar_base64 = get_image_base64("my_logo.png")

# استایل CSS
st.markdown("""
    <style>
    .main { direction: rtl; text-align: right; }
    div[data-testid="stMetricValue"] { text-align: right; }
    .stDataFrame { direction: rtl; }
    .logo-container {
        display: flex; justify-content: space-between; align-items: center;
        margin-bottom: 20px; background-color: white; padding: 15px;
        border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .logo-img { width: 110px; height: auto; object-fit: contain; }
    .footer {
        position: fixed; left: 0; bottom: 0; width: 100%;
        background-color: #f8f9fa; color: #333; text-align: center;
        padding: 12px 0; font-weight: bold; font-size: 16px;
        border-top: 3px solid #2E7D32; z-index: 999;
    }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 3. بخش لوگوها و عنوان (Header)
# ==============================================================================
st.markdown(f"""
    <div class="logo-container">
        <img src="data:image/png;base64,{logo_faz_fidar_base64}" class="logo-img">
        <h1 style='text-align: center; flex-grow: 1; color: #1E3A8A; font-size: 26px; margin: 0;'>📊 داشبورد جامع پایش ارتعاشات و بالانس - سیمان تهران</h1>
        <img src="data:image/png;base64,{logo_siman_base64}" class="logo-img">
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ==============================================================================
# 4. اتصال به منبع داده
# ==============================================================================
sheet_url = "https://docs.google.com/spreadsheets/d/1H4Yf3ilu72hl7YZns6EXNMpOfh-Eli98_sEO_81uXrs/export?format=csv&gid=0"

@st.cache_data(ttl=60)
def load_data(url):
    try:
        return pd.read_csv(url)
    except:
        return None

df = load_data(sheet_url)

if df is not None:
    st.success("✅ خوش آمدید. اطلاعات با موفقیت به‌روزرسانی شد!")

    st.subheader("📋 جدول جامع داده‌های ارتعاشات و بالانس")
    st.dataframe(df, use_container_width=True)

    st.markdown("---")
    st.subheader("📈 شاخص‌های کلیدی")
    col1, col2 = st.columns(2)

    with col1:
        if "بالانس" in df.columns:
            balance_numeric = pd.to_numeric(df["بالانس"], errors='coerce').fillna(0)
            st.metric(label="جمع کل بالانس‌ها (کل دوره)", value=f"{balance_numeric.sum():.2f}")

    with col2:
        if "mm/s" in df.columns:
            vibration_numeric = pd.to_numeric(df["mm/s"], errors='coerce')
            st.metric(label="حداکثر ارتعاش ثبت شده (mm/s)", value=f"{vibration_numeric.max():.2f}")

    st.markdown("---")
    st.subheader("📅 گزارش جمع بالانس سالانه")

    date_column = "تاریخ" 
    if date_column in df.columns:
        try:
            df_copy = df.copy()
            df_copy[date_column] = df_copy[date_column].ffill()
            df_copy['Year'] = df_copy[date_column].astype(str).str.split('/').str[-1].str.strip()
            years = df_copy['Year'].unique().tolist()

            if years and years[0] != 'nan':
                selected_year = st.selectbox("سال مورد نظر را انتخاب کنید:", years)
                yearly_df = df_copy[df_copy['Year'] == selected_year]
                yearly_sum = pd.to_numeric(yearly_df["بالانس"], errors='coerce').sum()
                st.info(f"مجموع مقادیر بالانس برای سال {selected_year} برابر است با: {yearly_sum:.2f}")

                with st.expander(f"مشاهده جزئیات داده‌های سال {selected_year}"):
                    st.dataframe(yearly_df.drop(columns=['Year']), use_container_width=True)
        except:
            pass

    st.markdown('<div class="footer">طراحی و توسعه: مهندس هادی زندیه | شرکت فاز فیدار پارسیان</div>', unsafe_allow_html=True)

else:
    st.error("❌ خطا در بارگذاری داده‌ها. لطفاً دسترسی شیت را بررسی کنید.")
