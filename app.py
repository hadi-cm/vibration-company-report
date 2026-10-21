import streamlit as st
import pandas as pd
# تنظیمات صفحه
st.set_page_config(page_title="سامانه پایش ارتعاشات - فاز فیدار پارسیان", layout="wide")
# --- بخش لوگو و هدر ---
col_logo, col_title, col_empty = st.columns([1, 4, 1])
with col_logo:
    try:
        st.image("logo.png", width=150) 
    except:
        pass
with col_title:
    st.markdown("<h2 style='text-align: center; color: #333333; margin-bottom: 0;'>📊 سامانه هوشمند پایش وضعیت ارتعاشات تجهیزات</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888888; font-size: 16px;'>توسعه‌دهنده: 💻 مهندس هادی زندیه</p>", unsafe_allow_html=True)
st.divider()
# آدرس گوگل شیت
SHEET_URL = "https://docs.google.com/spreadsheets/d/1H4Yf3ilu72hI7YZns6EXNMpOfH-EII98_sEO_81uXrs/export?format=csv&gid=0"
@st.cache_data(ttl=60)
def load_data():
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = ['تاریخ', 'خط تولید', 'واحد', 'عنوان تجهیز', 'تصویر تجهیز', 'محل اندازه گیری', 'عمودی', 'افقی', 'محوری', 'واحد اندازه گیری', 'توضیحات', 'دمای تجهیز', 'تناژ یا بارخور', 'دور تجهیز', 'وضعیت']
        df = df[~df['تاریخ'].astype(str).str.contains('تاریخ')]
        df['خط تولید'] = df['خط تولید'].ffill().apply(lambda x: str(int(x)) if isinstance(x, (int, float)) or (isinstance(x, str) and x.replace('.','').isdigit()) else str(x))
        cols_to_fill = ['تاریخ', 'واحد', 'عنوان تجهیز', 'تصویر تجهیز']
        df[cols_to_fill] = df[cols_to_fill].ffill()
        for c in ['عمودی', 'افقی', 'محوری']:
            df[c] = pd.to_numeric(df[c], errors='coerce')
        return df
    except Exception as e:
        return None
def color_vibration(val):
    if pd.isna(val): return ''
    if val > 7.2: return 'background-color: #ffcccc; color: black'
    if val >= 4.7: return 'background-color: #ffffcc; color: black'
    return ''
def color_status_text(val):
    val_str = str(val)
    if 'هشدار' in val_str: return 'background-color: #ffcccc; color: black'
    if 'مراقبت' in val_str: return 'background-color: #ffffcc; color: black'
    if 'نرمال' in val_str: return 'background-color: #ccffcc; color: black'
    return ''
df = load_data()
if df is not None:
    all_lines = df['خط تولید'].dropna().unique().tolist()
    selected_lines = st.sidebar.multiselect("انتخاب خط تولید", all_lines, default=all_lines)
    for line in selected_lines:
        line_data = df[df['خط تولید'] == line]
        st.header(f"🏢 خط تولید: {line}")
        for eq in line_data['عنوان تجهیز'].unique():
            eq_data = line_data[line_data['عنوان تجهیز'] == eq].dropna(subset=['عمودی', 'افقی', 'محوری'], how='all')
            if eq_data.empty: continue
            img_url = eq_data['تصویر تجهیز'].iloc[0]
            col_eq_text, col_eq_img = st.columns([4, 1])
            with col_eq_text:
                st.subheader(f"📦 تجهیز: {eq}")
            with col_eq_img:
                if pd.notna(img_url) and str(img_url).startswith('http'):
                    st.image(img_url, width=100)
                else:
                    st.write("📷 بدون عکس")
            display_cols = ['محل اندازه گیری', 'عمودی', 'افقی', 'محوری', 'دمای تجهیز', 'تناژ یا بارخور', 'دور تجهیز', 'وضعیت']
            # --- اصلاح بخش فرمت‌بندی برای اضافه کردن واحدها ---
            df_display = eq_data[display_cols].copy()
            # اضافه کردن واحد درجه سانتی‌گراد به دما
            df_display['دمای تجهیز'] = df_display['دمای تجهیز'].apply(lambda x: f"{x}°C" if pd.notna(x) else "-")
            # اضافه کردن واحد تن بر ساعت به تناژ
            df_display['تناژ یا بارخور'] = df_display['تناژ یا بارخور'].apply(lambda x: f"{x} t/h" if pd.notna(x) else "-")
            styled_df = df_display.style.format({
                'عمودی': "{:.1f}", 'افقی': "{:.1f}", 'محوری': "{:.1f}"
            }, na_rep="-").map(color_vibration, subset=['عمودی', 'افقی', 'محوری']).map(color_status_text, subset=['وضعیت'])
            st.dataframe(styled_df, use_container_width=True, hide_index=True)
            st.write("---")
st.caption("تمامی حقوق متعلق به شرکت فاز فیدار پارسیان می‌باشد.")
