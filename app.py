import streamlit as st
import pandas as pd

st.set_page_config(page_title="سامانه گزارش ارتعاشات", layout="wide")

COMPANY_NAME = "گزارش پایش وضعیت ارتعاشات"
st.title(COMPANY_NAME)
st.caption("طراحی شده توسط هادی")
st.divider()

# آدرس گوگل شیت شما
SHEET_URL = "https://docs.google.com/spreadsheets/d/1H4Yf3ilu72hI7YZns6EXNMpOfH-EII98_sEO_81uXrs/export?format=csv&gid=0"

@st.cache_data(ttl=60)
def load_data():
    try:
        # خواندن داده‌ها
        df = pd.read_csv(SHEET_URL)
        
        # نام‌گذاری مجدد ستون‌ها بر اساس ترتیب (برای جلوگیری از خطای نام تجهیز)
        df.columns = ['تاریخ', 'خط تولید', 'واحد', 'عنوان تجهیز', 'محل اندازه گیری', 'عمودی', 'افقی', 'محوری', 'واحد اندازه گیری', 'توضیحات', 'وضعیت']
        
        # حذف ردیف‌هایی که هدر تکراری هستند (مثل ردیف 14)
        df = df[~df['تاریخ'].astype(str).str.contains('تاریخ')]
        
        # پر کردن سلول‌های خالی (Merge شده در ظاهر)
        cols_to_fill = ['تاریخ', 'خط تولید', 'واحد', 'عنوان تجهیز']
        df[cols_to_fill] = df[cols_to_fill].ffill()
        
        return df
    except Exception as e:
        st.error(f"خطا در بارگذاری: {e}")
        return None

# تابع رنگ‌بندی اعداد
def color_vibration(val):
    try:
        num = float(val)
        if num > 7.2:
            return 'background-color: #ffcccc; color: black' # قرمز
        elif num >= 4.7:
            return 'background-color: #ffffcc; color: black' # زرد
    except:
        pass
    return ''

# تابع رنگ‌بندی وضعیت
def color_status_text(val):
    if 'هشدار' in str(val): return 'background-color: #ffcccc; color: black'
    if 'مراقبت' in str(val): return 'background-color: #ffffcc; color: black'
    if 'نرمال' in str(val): return 'background-color: #ccffcc; color: black'
    return ''

df = load_data()

if df is not None:
    # فیلترها در سایدبار
    st.sidebar.header("فیلترها")
    all_lines = df['خط تولید'].dropna().unique().tolist()
    selected_lines = st.sidebar.multiselect("انتخاب خط تولید", all_lines, default=all_lines)

    filtered_df = df[df['خط تولید'].isin(selected_lines)]

    for line in selected_lines:
        line_data = filtered_df[filtered_df['خط تولید'] == line]
        if line_data.empty: continue
        
        st.header(f"🏢 {line}")
        
        for eq in line_data['عنوان تجهیز'].unique():
            eq_data = line_data[line_data['عنوان تجهیز'] == eq]
            st.subheader(f"📦 تجهیز: {eq}")
            
            # انتخاب ستون‌های نمایش
            display_cols = ['محل اندازه گیری', 'عمودی', 'افقی', 'محوری', 'وضعیت']
            
            # اعمال رنگ‌بندی
            styled_df = eq_data[display_cols].style.map(color_vibration, subset=['عمودی', 'افقی', 'محوری']).map(color_status_text, subset=['وضعیت'])
            
            st.dataframe(styled_df, use_container_width=True)
            st.write("---")

st.caption("تمامی حقوق برای شرکت محفوظ است.")
