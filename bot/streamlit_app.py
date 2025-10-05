import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os

# Database importini sozlash
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_manager import DatabaseManager
from config import SUBSCRIPTION_PLANS

# Sahifa konfiguratsiyasi
st.set_page_config(
    page_title="Kutubxona Dashboard",
    page_icon="📚",
    layout="wide"
)


# Autentifikatsiya
def check_password():
    """Admin parolini tekshirish"""

    def password_entered():
        if st.session_state["password"] == "qwerty":  # O'zgartiring!
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input(
            "Parol",
            type="password",
            on_change=password_entered,
            key="password"
        )
        st.write("*Admin paroli: admin*")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input(
            "Parol",
            type="password",
            on_change=password_entered,
            key="password"
        )
        st.error("😕 Noto'g'ri parol")
        return False
    else:
        return True


if not check_password():
    st.stop()

# CSS stillari
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# Sarlavha
st.title("📚 Kutubxona Boshqaruv Tizimi")
st.markdown("---")

# Database ulanish
db = DatabaseManager()

# Refresh tugmasi
col1, col2, col3 = st.columns([1, 1, 4])
with col1:
    if st.button("🔄 Yangilash"):
        st.rerun()

# Asosiy statistika
st.header("📊 Asosiy Statistika")

stats = db.get_statistics()
all_users = db.get_all_users()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="👥 Jami Foydalanuvchilar",
        value=stats['total_users']
    )

with col2:
    st.metric(
        label="📗 Free",
        value=stats['free_users']
    )

with col3:
    st.metric(
        label="📘 Money",
        value=stats['money_users']
    )

with col4:
    st.metric(
        label="📕 Premium",
        value=stats['premium_users']
    )

st.markdown("---")

# Grafiklar
st.header("📈 Vizual Tahlil")

col1, col2 = st.columns(2)

with col1:
    # Tarif bo'yicha taqsimot
    fig_plans = go.Figure(data=[go.Pie(
        labels=['Free', 'Money', 'Premium'],
        values=[stats['free_users'], stats['money_users'], stats['premium_users']],
        hole=.3,
        marker_colors=['#90EE90', '#87CEEB', '#FFB6C1']
    )])
    fig_plans.update_layout(title_text="Tariflar bo'yicha taqsimot")
    st.plotly_chart(fig_plans, use_container_width=True)

with col2:
    # Yosh guruhlari
    if all_users:
        ages = [user.age for user in all_users]
        age_groups = pd.cut(ages, bins=[0, 18, 30, 50, 100], labels=['0-18', '19-30', '31-50', '50+'])
        age_df = pd.DataFrame({'Yosh guruhi': age_groups.value_counts().index,
                               'Soni': age_groups.value_counts().values})

        fig_age = px.bar(age_df, x='Yosh guruhi', y='Soni',
                         title="Yosh guruhlari bo'yicha taqsimot",
                         color='Soni')
        st.plotly_chart(fig_age, use_container_width=True)

st.markdown("---")

# Foydalanuvchilar jadvali
st.header("👥 Foydalanuvchilar Ro'yxati")

if all_users:
    # Filtrlar
    col1, col2, col3 = st.columns(3)

    with col1:
        search_id = st.text_input("🔍 ID bo'yicha qidirish", "")

    with col2:
        search_name = st.text_input("🔍 Ism bo'yicha qidirish", "")

    with col3:
        filter_plan = st.selectbox(
            "📋 Tarif bo'yicha filtr",
            ["Barchasi", "Free", "Money", "Premium"]
        )

    # Ma'lumotlarni DataFrame ga aylantirish
    users_data = []
    for user in all_users:
        status = "✅ Aktiv" if user.is_active else "❌ Aktiv emas"
        days_left = ""

        if user.subscription_end_date:
            days = (user.subscription_end_date - datetime.now()).days
            days_left = f"{days} kun" if days > 0 else "Tugagan"

        users_data.append({
            "ID": user.library_id,
            "Ism": f"{user.first_name}" ,# {user.last_name}",
            "Familiya": user.last_name,
            "Yosh": user.age,
            "Telefon": user.phone_number,
            "Tarif": user.subscription_plan,
            "Qolgan muddat": days_left if days_left else "Cheksiz",
            "Status": status,
            "Ro'yxatdan o'tgan": user.registered_date.strftime("%d.%m.%Y")
        })

    df = pd.DataFrame(users_data)

    # Filtrlash
    if search_id:
        df = df[df['ID'].str.contains(search_id, case=False)]

    if search_name:
        df = df[df['Ism'].str.contains(search_name, case=False)]

    if filter_plan != "Barchasi":
        df = df[df['Tarif'] == filter_plan]

    # Jadvalni ko'rsatish
    st.dataframe(df, use_container_width=True, height=400)

    # Excel yuklab olish
    csv = df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 Excel yuklab olish",
        data=csv,
        file_name=f"kutubxona_users_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

else:
    st.info("Hozircha foydalanuvchilar yo'q")

st.markdown("---")

# Tarif o'zgartirish (Admin uchun)
st.header("⚙️ Tarif Boshqaruvi")

with st.expander("✏️ Foydalanuvchi tarifini o'zgartirish"):
    col1, col2 = st.columns(2)

    with col1:
        user_id_to_update = st.text_input("Foydalanuvchi ID", placeholder="ID0001")

    with col2:
        new_plan = st.selectbox("Yangi tarif", ["Free", "Money", "Premium"])

    if st.button("✅ Tarifni o'zgartirish"):
        if user_id_to_update:
            user = db.get_user_by_library_id(user_id_to_update)

            if user:
                success = db.update_subscription(user_id_to_update, new_plan)

                if success:
                    st.success(
                        f"✅ {user.first_name} {user.last_name} ({user_id_to_update}) ning tarifi {new_plan}ga o'zgartirildi!")
                    st.rerun()
                else:
                    st.error("❌ Xatolik yuz berdi!")
            else:
                st.error(f"❌ {user_id_to_update} ID raqamli foydalanuvchi topilmadi!")
        else:
            st.warning("⚠️ Iltimos, foydalanuvchi ID sini kiriting!")

st.markdown("---")

# Ogohlantirish kerak bo'lgan foydalanuvchilar
st.header("⚠️ Ogohlantirish Kerak Bo'lgan Foydalanuvchilar")

warning_users = db.get_users_needing_warning()

if warning_users:
    warning_data = []
    for user in warning_users:
        days_left = (user.subscription_end_date - datetime.now()).days
        warning_data.append({
            "ID": user.library_id,
            "Ism": f"{user.first_name} {user.last_name}",
            "Telefon": user.phone_number,
            "Tarif": user.subscription_plan,
            "Qolgan kunlar": days_left,
            "Tugash sanasi": user.subscription_end_date.strftime("%d.%m.%Y")
        })

    warning_df = pd.DataFrame(warning_data)
    st.dataframe(warning_df, use_container_width=True)
else:
    st.success("✅ Ogohlantirish kerak bo'lgan foydalanuvchilar yo'q")

# Database yopish
db.close()

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
        📚 Kutubxona Boshqaruv Tizimi | Ishlab chiqilgan: 2024
    </div>
    """,
    unsafe_allow_html=True
)