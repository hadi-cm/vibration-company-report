import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- ۱. تنظیمات اولیه صفحه ---
st.set_page_config(page_title="سامانه جامع پایش وضعیت - فیدارفارسیان", layout="wide", page_icon="🛠️")

# --- ۲. سیستم تایید ایمیل ---
def check_email_access():
        allowed_emails = ["vah.rezaei@gmail.com", "alireza76ir@gmail.com", "hamidreza.doroud@gmail.com", "masoud.sa.1989823@gmail.com"]
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if not st.session_state["authenticated"]:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("<h2 style='text-align: center; color: #2c3e50;'>🔐 ورود به سامانه پایش وضعیت</h2>", unsafe_allow_html=True)
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
    st.stop()

# --- ۳. استایل‌های CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@100;400;700&display=swap');
    html, body, [class=" css"]  { font-family: 'Vazirmatn', sans-serif !important; direction: rtl; text-align: right; }
    .main { text-align: right; }
    .header-text { text-align: center; width: 100%; }
    </style>
    """, unsafe_allow_html=True)
# --- ۴. هدر ---
col_me, col_title, col_client = st.columns([1, 3, 1])
with col_client:
    try: st.image("client_logo.png", width=130)
    except: st.info("لوگوی کارفرما")
with col_title:
    st.markdown("<div class='header-text'><h2 style='color: #2c3e50;'>🛠️ سامانه هوشمند تحلیل روند و پایش ارتعاشات تجهیزات</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #7f8c8d;'>مدیریت متمرکز پایش وضعیت و تاریخچه تعمیرات - مهندس هادی زندیه</p></div>", unsafe_allow_html=True)
with col_me:
    try: st.image("my_logo.png", width=130)
    except: st.info("لوگوی مهندس هادی")
st.divider()
# --- ۵. بارگذاری داده‌ها ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/1H4Yf3ilu72hI7YZns6EXNMpOfH-EII98_sEO_81uXrs/export?format=csv&gid=0"
@st.cache_data(ttl=60)
def load_data():
    try:
        df = pd.read_csv(SHEET_URL)
        # توجه: نام ستون‌ها را مطابق با تغییرات شما در گوگل شیت تنظیم کنید
        # من ستون 'اولویت' را به انتهای لیست اضافه کردم
        df.columns = ['تاریخ', 'خط تولید', 'واحد', 'عنوان تجهیز', 'تصویر تجهیز', 'محل اندازه گیری', 'عمودی', 'افقی', 'محوری', 'واحد اندازه گیری', 'دور تجهیز', 'دمای تجهیز', 'تناژ یا بارخور', 'توضیحات', 'وضعیت', 'اقدام اصلاحی', 'هزینه', 'اولویت']
        df = df[df['تاریخ'].astype(str) != 'تاریخ']
        df[['تاریخ', 'خط تولید', 'عنوان تجهیز']] = df[['تاریخ', 'خط تولید', 'عنوان تجهیز']].ffill()
        numeric_cols = ['عمودی', 'افقی', 'محوری', 'دور تجهیز', 'دمای تجهیز', 'تناژ یا بارخور', 'هزینه']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        return df
    except Exception as e:
        st.error(f"خطا در بارگذاری داده‌ها: {e}")
        return None
def color_vibration(val):
    if not isinstance(val, (int, float)) or val == 0: return ''
    if val > 7.2: return 'background-color: #ffcccc; color: black'
    if val >= 4.7: return 'background-color: #ffffcc; color: black'
    return ''
def color_priority(val):
    if 'اول' in str(val): return 'background-color: #ff0000; color: white; font-weight: bold'
    if 'دوم' in str(val): return 'background-color: #ffff00; color: black; font-weight: bold'
    if 'سوم' in str(val): return 'background-color: #ccffcc; color: black; font-weight: bold'
    return ''
df = load_data()
if df is not None:
    st.sidebar.header("🧭 منوی مدیریت سامانه")
    app_mode = st.sidebar.selectbox("انتخاب بخش", ["🚨 لیست اولویت‌های تعمیراتی", "📊 تحلیل مقایسه‌ای تجهیزات", "📈 تحلیل روند و پرونده تجهیز", "💰 گزارش مالی و تعمیرات"])
    all_lines = df['خط تولید'].dropna().unique().tolist()
    selected_line = st.sidebar.selectbox("🏢 انتخاب واحد/خط تولید", all_lines)
    line_df = df[df['خط تولید'] == selected_line]
    # --- بخش جدید: لیست اولویت‌های تعمیراتی (بر اساس عکس شما) ---
    if app_mode == "🚨 لیست اولویت‌های تعمیراتی":
        st.header(f"🚨 اولویت‌های اقدام تعمیراتی - {selected_line}")
        # فیلتر کردن داده‌ها برای نمایش فقط موارد دارای اولویت
        priority_df = line_df[line_df['اولویت'].notna()].sort_values('اولویت')
        if not priority_df.empty:
            # انتخاب ستون‌های مورد نیاز برای نمایش در جدول (عنوان تجهیز + توضیحات/اقدام اصلاحی + اولویت)
            display_df = priority_df[['عنوان تجهیز', 'توضیحات', 'اولویت']].copy()
            display_df.columns = ['تجهیز', 'توضیحات فنی و نیاز به اقدام', 'درجه اولویت']
            # اعمال رنگ‌بندی روی ستون اولویت
            st.dataframe(
                display_df.style.map(color_priority, subset=['درجه اولویت']), 
                use_container_width=True, 
                hide_index=True
            )
            st.info("💡 رنگ قرمز: اقدام فوری | رنگ زرد: اولین فرصت | رنگ سبز: زمان تعمیرات")
        else:
            st.warning("در حال حاضر هیچ موردی در لیست اولویت‌ها ثبت نشده است.")
    # --- بخش اول: تحلیل مقایسه‌ای ---
    elif app_mode == "📊 تحلیل مقایسه‌ای تجهیزات":
        st.header(f"🔍 تحلیل تاریخچه ارتعاشات - {selected_line}")
        all_eqs_in_line = line_df['عنوان تجهیز'].unique().tolist()
        if all_eqs_in_line:
            selected_eq = st.selectbox("📦 انتخاب تجهیز مورد نظر", all_eqs_in_line)
            eq_data = line_df[line_df['عنوان تجهیز'] == selected_eq].sort_values('تاریخ')
            if not eq_data.empty:
                pivot_df = eq_data.pivot_table(index='تاریخ', columns='محل اندازه گیری', values='عمودی', aggfunc='first').fillna(0)
                st.dataframe(pivot_df.style.map(color_vibration).format("{:.2f}"), use_container_width=True)
                img_url = eq_data['تصویر تجهیز'].iloc[0]
                if pd.notna(img_url) and str(img_url).startswith('http'):
                    st.image(img_url, caption=f"تصویر {selected_eq}", width=250)
    # --- بخش دوم: تحلیل روند ---
    elif app_mode == "📈 تحلیل روند و پرونده تجهیز":
        st.header("📂 پرونده دیجیتال و تحلیل روند تجهیزات")
        all_eqs = line_df['عنوان تجهیز'].unique().tolist()
        if all_eqs:
            selected_eq = st.selectbox("🔍 انتخاب تجهیز برای تحلیل سالانه", all_eqs)
            eq_history = line_df[line_df['عنوان تجهیز'] == selected_eq].sort_values('تاریخ')
            if not eq_history.empty:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=eq_history['تاریخ'], y=eq_history['عمودی'], name='عمودی', line=dict(color='blue', width=3)))
                fig.add_trace(go.Scatter(x=eq_history['تاریخ'], y=eq_history['افقی'], name='افقی', line=dict(color='green', width=3)))
                fig.add_trace(go.Scatter(x=eq_history['تاریخ'], y=eq_history['محوری'], name='محوری', line=dict(color='red', width=3)))
                events = eq_history[eq_history['اقدام اصلاحی'].notna() & (eq_history['اقدام اصلاحی'] != "")]
                if not events.empty:
                    fig.add_trace(go.Scatter(x=events['تاریخ'], y=events['عمودی'], mode='markers+text', text=events['اقدام اصلاحی'], textposition="top center", marker=dict(color='orange', size=14, symbol='diamond'), name='اقدامات تعمیراتی'))
                fig.update_layout(title=f"روند تغییرات ارتعاشات {selected_eq}", xaxis_title="تاریخ", yaxis_title="مقدار ارتعاش", template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(eq_history[['تاریخ', 'محل اندازه گیری', 'دور تجهیز', 'تناژ یا بارخور', 'اقدام اصلاحی', 'هزینه', 'توضیحات']], hide_index=True, use_container_width=True)
    # --- بخش سوم: گزارش مالی ---
    elif app_mode == "💰 گزارش مالی و تعمیرات":
        st.header(f"💸 تحلیل هزینه‌ها - {selected_line}")
        total_cost = line_df['هزینه'].sum()
        st.metric("مجموع هزینه‌های تعمیراتی این واحد", f"{total_cost:,.0f} تومان")
        cost_per_eq = line_df.groupby('عنوان تجهیز')['هزینه'].sum().sort_values(ascending=False).reset_index()
        if not cost_per_eq.empty:
            st.bar_chart(cost_per_eq.set_index('عنوان تجهیز'))
st.caption("تمامی حقوق متعلق به شرکت فیدار پارسیان می‌باشد. | طراحی و توسعه: مهندس هادی زندیه")
