import streamlit as st
import pandas as pd
import plotly.graph_objects as go
# تنظیمات صفحه
st.set_page_config(page_title="سامانه جامع پایش وضعیت - فیدارفارسیان", layout="wide")
# --- استایل‌های CSS برای راست‌چین کردن و بهینه‌سازی ---
st.markdown("""
    <style>
    .main { text-align: right; }
    .header-text { text-align: center; width: 100%; }
    .stDataFrame { text-align: right; }
    div[data-testid="stExpander"] { text-align: right; }
    </style>
    """, unsafe_allow_html=True)
# --- هدر (کارفرما راست - من چپ) ---
col_me, col_title, col_client = st.columns([1, 3, 1])
with col_client:
    try:
        st.image("client_logo.png", width=130)
    except:
        st.info("لوگوی کارفرما")
with col_title:
    st.markdown("<div class='header-text'><h2 style='color: #2c3e50;'>🛠️ سامانه هوشمند تحلیل روند و پایش ارتعاشات تجهیزات</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #7f8c8d;'>مدیریت متمرکز پایش وضعیت و تاریخچه تعمیرات - مهندس هادی زندیه</p></div>", unsafe_allow_html=True)
with col_me:
    try:
        st.image("my_logo.png", width=130)
    except:
        st.info("لوگوی مهندس هادی")
st.divider()
# --- بارگذاری داده‌ها از گوگل شیت ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/1H4Yf3ilu72hI7YZns6EXNMpOfH-EII98_sEO_81uXrs/export?format=csv&gid=0"
@st.cache_data(ttl=60)
def load_data():
    try:
        df = pd.read_csv(SHEET_URL)
        # نام‌گذاری ستون‌ها برای اطمینان از صحت داده‌ها
        df.columns = ['تاریخ', 'خط تولید', 'واحد', 'عنوان تجهیز', 'تصویر تجهیز', 'محل اندازه گیری', 'عمودی', 'افقی', 'محوری', 'واحد اندازه گیری', 'دور تجهیز', 'دمای تجهیز', 'تناژ یا بارخور', 'توضیحات', 'وضعیت', 'اقدام اصلاحی', 'هزینه']
        # حذف سطرهای تکراری یا خالی در ستون تاریخ
        df = df[df['تاریخ'].astype(str) != 'تاریخ']
        # پر کردن جاهای خالی در ستون‌های اصلی (Forward Fill)
        df[['تاریخ', 'خط تولید', 'عنوان تجهیز']] = df[['تاریخ', 'خط تولید', 'عنوان تجهیز']].ffill()
        # تبدیل ستون‌های عددی
        numeric_cols = ['عمودی', 'افقی', 'محوری', 'دور تجهیز', 'دمای تجهیز', 'تناژ یا بارخور', 'هزینه']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        return df
    except Exception as e:
        st.error(f"خطا در بارگذاری داده‌ها: {e}")
        return None
# تابع رنگ‌بندی ارتعاشات
def color_vibration(val):
    if not isinstance(val, (int, float)) or val == 0: 
        return ''
    if val > 7.2: return 'background-color: #ffcccc; color: black' # قرمز (بحرانی)
    if val >= 4.7: return 'background-color: #ffffcc; color: black' # زرد (هشدار)
    return ''
df = load_data()
if df is not None:
    # --- سایدبار (منوی مدیریت) ---
    st.sidebar.header("🧭 منوی مدیریت سامانه")
    app_mode = st.sidebar.selectbox("انتخاب بخش", ["📊 تحلیل مقایسه‌ای تجهیزات", "📈 تحلیل روند و پرونده تجهیز", "💰 گزارش مالی و تعمیرات"])
    # تفکیک بر اساس خط تولید در سایدبار (برای مدیریت ۱۵۰ تجهیز)
    all_lines = df['خط تولید'].dropna().unique().tolist()
    selected_line = st.sidebar.selectbox("🏢 انتخاب واحد/خط تولید", all_lines)
    # فیلتر داده‌ها بر اساس خط تولید انتخاب شده
    line_df = df[df['خط تولید'] == selected_line]
    # -------------------------------------------------------------------------
    # بخش اول: تحلیل مقایسه‌ای تاریخچه
    # -------------------------------------------------------------------------
    if app_mode == "📊 تحلیل مقایسه‌ای تجهیزات":
        st.header(f"🔍 تحلیل تاریخچه ارتعاشات - {selected_line}")
        st.info("در این بخش، تاریخ‌های مختلف در سطرها و نقاط اندازه‌گیری در ستون‌ها قرار گرفته‌اند تا روند تغییرات هر نقطه در طول زمان مشخص شود.")
        all_eqs_in_line = line_df['عنوان تجهیز'].unique().tolist()
        # انتخاب تجهیز (به دلیل تعداد زیاد تجهیزات در هر خط)
        selected_eq = st.selectbox("📦 انتخاب تجهیز مورد نظر", all_eqs_in_line)
        # استخراج داده‌های مربوط به تجهیز انتخاب شده و مرتب‌سازی بر اساس تاریخ
        eq_data = line_df[line_df['عنوان تجهیز'] == selected_eq].sort_values('تاریخ')
        if not eq_data.empty:
            # ساخت جدول ماتریسی: سطر=تاریخ، ستون=محل اندازه گیری، مقدار=عمودی
            pivot_df = eq_data.pivot_table(
                index='تاریخ', 
                columns='محل اندازه گیری', 
                values='عمودی'
            ).fillna(0)
            # اضافه کردن اطلاعات وضعیت و اقدام اصلاحی به هر تاریخ
            status_info = eq_data.set_index('تاریخ')['وضعیت']
            action_info = eq_data.set_index('تاریخ')['اقدام اصلاحی']
            final_table = pivot_df.copy()
            final_table['وضعیت'] = status_info
            final_table['اقدام اصلاحی'] = action_info
            st.subheader(f"📅 جدول مقایسه‌ای تاریخچه ارتعاشات: {selected_eq}")
            st.dataframe(
                final_table.style.map(color_vibration), 
                use_container_width=True
            )
            # نمایش تصویر تجهیز
            img_url = eq_data['تصویر تجهیز'].iloc[0]
            if pd.notna(img_url) and str(img_url).startswith('http'):
                st.image(img_url, caption=f"تصویر {selected_eq}", width=250)
        else:
            st.warning("داده‌ای برای این تجهیز یافت نشد.")
    # -------------------------------------------------------------------------
    # بخش دوم: تحلیل روند و پرونده دیجیتال
    # -------------------------------------------------------------------------
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
                    fig.add_trace(go.Scatter(x=events['تاریخ'], y=events['عمودی'], mode='markers+text', 
                                             text=events['اقدام اصلاحی'], textposition="top center",
                                             marker=dict(color='orange', size=14, symbol='diamond'), name='اقدامات تعمیراتی'))
                fig.update_layout(title=f"روند تغییرات ارتعاشات {selected_eq}", xaxis_title="تاریخ", yaxis_title="مقدار ارتعاش", template="plotly_white")
                st.plotly_chart(fig, use_container_width=True)
                st.subheader("📝 تاریخچه فنی و اقدامات ثبت شده")
                st.dataframe(eq_history[['تاریخ', 'محل اندازه گیری', 'دور تجهیز', 'تناژ یا بارخور', 'اقدام اصلاحی', 'هزینه', 'توضیحات']], hide_index=True, use_container_width=True)
    # -------------------------------------------------------------------------
    # بخش سوم: گزارش مالی و تعمیرات
    # -------------------------------------------------------------------------
    elif app_mode == "💰 گزارش مالی و تعمیرات":
        st.header(f"💸 تحلیل هزینه‌ها - {selected_line}")
        total_cost = line_df['هزینه'].sum()
        st.metric("مجموع هزینه‌های تعمیراتی این واحد", f"{total_cost:,.0f} تومان")
        st.subheader("🔝 تجهیزات پرهزینه در این واحد (Bad Actors)")
        cost_per_eq = line_df.groupby('عنوان تجهیز')['هزینه'].sum().sort_values(ascending=False).reset_index()
        if not cost_per_eq.empty:
            st.bar_chart(cost_per_eq.set_index('عنوان تجهیز'))
st.caption("تمامی حقوق متعلق به شرکت فیدار پارسیان می‌باشد. | طراحی و توسعه: مهندس هادی زندیه")
