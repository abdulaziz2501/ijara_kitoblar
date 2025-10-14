import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os
from collections import Counter

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
        if st.session_state["password"] == "admin":  # O'zgartiring!
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


def categorize_study_place(study_place: str) -> str:
    """O'quv joyini kategoriyaga ajratish"""
    if not study_place or study_place == "Kiritilmagan":
        return "Kiritilmagan"

    study_place_lower = study_place.lower()

    # Universitet
    university_keywords = ['universitet', 'university', 'institute', 'institut', 'davlat', 'milliy']
    if any(keyword in study_place_lower for keyword in university_keywords):
        return "🎓 Universitet"

    # Kollej
    college_keywords = ['kollej', 'college', 'texnikum', 'akademiya', 'akademik']
    if any(keyword in study_place_lower for keyword in college_keywords):
        return "🏫 Kollej"

    # Maktab
    school_keywords = ['maktab', 'school', 'litsey', 'gimnaziya']
    if any(keyword in study_place_lower for keyword in school_keywords):
        return "🏫 Maktab"

    # Ishchi yoki boshqa
    work_keywords = ['ishlash', 'ish', 'kompaniya', 'firma', 'korxona']
    if any(keyword in study_place_lower for keyword in work_keywords):
        return "💼 Ishchi"

    # Ishlamayman
    if 'ishlamayman' in study_place_lower or 'yo\'q' in study_place_lower:
        return "🏠 Ishlamayman"

    return "📋 Boshqa"


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
    .category-card {
        padding: 1rem;
        border-radius: 0.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin: 0.5rem 0;
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

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        label="👥 Jami",
        value=stats['total_users']
    )

with col2:
    st.metric(
        label="🟢 Free",
        value=stats['free_users']
    )

with col3:
    st.metric(
        label="🔵 Money",
        value=stats['money_users']
    )

with col4:
    st.metric(
        label="🟣 Premium",
        value=stats['premium_users']
    )

with col5:
    st.metric(
        label="📈 O'rtacha yosh",
        value=f"{stats['average_age']}"
    )

st.markdown("---")

# O'quv joylari statistikasi
st.header("🎓 O'quv Joylari Bo'yicha Statistika")

if all_users:
    # O'quv joylarini kategoriyalash
    study_categories = [categorize_study_place(user.study_place) for user in all_users]
    category_counts = Counter(study_categories)

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        st.metric("🎓 Universitet", category_counts.get("🎓 Universitet", 0))

    with col2:
        st.metric("🏫 Kollej", category_counts.get("🏫 Kollej", 0))

    with col3:
        st.metric("🏫 Maktab", category_counts.get("🏫 Maktab", 0))

    with col4:
        st.metric("💼 Ishchi", category_counts.get("💼 Ishchi", 0))

    with col5:
        st.metric("🏠 Ishlamayman", category_counts.get("🏠 Ishlamayman", 0))

    with col6:
        st.metric("📋 Boshqa", category_counts.get("📋 Boshqa", 0) + category_counts.get("Kiritilmagan", 0))

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
    fig_plans.update_layout(
        title_text="Tariflar bo'yicha taqsimot",
        showlegend=True
    )
    st.plotly_chart(fig_plans, use_container_width=True)

with col2:
    # O'quv joylari bo'yicha taqsimot
    if all_users:
        category_df = pd.DataFrame({
            'Kategoriya': list(category_counts.keys()),
            'Soni': list(category_counts.values())
        })

        fig_study = px.bar(
            category_df,
            x='Kategoriya',
            y='Soni',
            title="O'quv joylari bo'yicha taqsimot",
            color='Soni',
            color_continuous_scale='Viridis'
        )
        fig_study.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_study, use_container_width=True)

# Yosh va tarif bo'yicha tahlil
st.subheader("📊 Yosh va Tarif Tahlili")
col1, col2 = st.columns(2)

with col1:
    # Yosh guruhlari
    if all_users:
        ages = [user.age for user in all_users]
        age_groups = pd.cut(ages, bins=[0, 18, 25, 35, 50, 100],
                            labels=['0-18', '19-25', '26-35', '36-50', '50+'])
        age_df = pd.DataFrame({
            'Yosh guruhi': age_groups.value_counts().index,
            'Soni': age_groups.value_counts().values
        })

        fig_age = px.bar(
            age_df,
            x='Yosh guruhi',
            y='Soni',
            title="Yosh guruhlari bo'yicha taqsimot",
            color='Soni',
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig_age, use_container_width=True)

with col2:
    # Kategoriya va tarif kesishishi
    if all_users:
        category_plan_data = []
        for user in all_users:
            category = categorize_study_place(user.study_place)
            category_plan_data.append({
                'Kategoriya': category,
                'Tarif': user.subscription_plan
            })

        cp_df = pd.DataFrame(category_plan_data)
        cp_pivot = cp_df.groupby(['Kategoriya', 'Tarif']).size().reset_index(name='Soni')

        fig_cp = px.bar(
            cp_pivot,
            x='Kategoriya',
            y='Soni',
            color='Tarif',
            title="Kategoriya va Tarif kesishishi",
            barmode='stack',
            color_discrete_map={'Free': '#90EE90', 'Money': '#87CEEB', 'Premium': '#FFB6C1'}
        )
        fig_cp.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_cp, use_container_width=True)

st.markdown("---")

# Foydalanuvchilar jadvali
st.header("👥 Foydalanuvchilar Ro'yxati")

if all_users:
    # Filtrlar
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        search_id = st.text_input("🔍 ID bo'yicha qidirish", "")

    with col2:
        search_name = st.text_input("🔍 Ism bo'yicha qidirish", "")

    with col3:
        filter_plan = st.selectbox(
            "📋 Tarif bo'yicha filtr",
            ["Barchasi", "Free", "Money", "Premium"]
        )

    with col4:
        filter_category = st.selectbox(
            "🎓 O'quv joyi bo'yicha filtr",
            ["Barchasi", "🎓 Universitet", "🏫 Kollej", "🏫 Maktab",
             "💼 Ishchi", "🏠 Ishlamayman", "📋 Boshqa"]
        )

    # Ma'lumotlarni DataFrame ga aylantirish
    users_data = []
    for user in all_users:
        status = "✅ Aktiv" if user.is_active else "❌ Aktiv emas"
        days_left = ""

        if user.subscription_end_date:
            days = (user.subscription_end_date - datetime.now()).days
            days_left = f"{days} kun" if days > 0 else "Tugagan"

        category = categorize_study_place(user.study_place)

        users_data.append({
            "ID": user.library_id,
            "Ism": user.first_name,
            "Familiya": user.last_name,
            "Yosh": user.age,
            "O'quv joyi": user.study_place,
            "Kategoriya": category,
            "Telefon": user.phone_number,
            "Tarif": user.subscription_plan,
            "Qolgan muddat": days_left if days_left else "Cheksiz",
            "Status": status
        })

    df = pd.DataFrame(users_data)

    # Filtrlash
    if search_id:
        df = df[df['ID'].str.contains(search_id, case=False)]

    if search_name:
        mask = df['Ism'].str.contains(search_name, case=False, na=False) | \
               df['Familiya'].str.contains(search_name, case=False, na=False)
        df = df[mask]

    if filter_plan != "Barchasi":
        df = df[df['Tarif'] == filter_plan]

    if filter_category != "Barchasi":
        df = df[df['Kategoriya'] == filter_category]

    # Statistika ko'rsatish
    st.info(f"📊 Ko'rsatilgan: {len(df)} ta foydalanuvchi")

    # Jadvalni ko'rsatish
    st.dataframe(
        df,
        use_container_width=True,
        height=400,
        column_config={
            "ID": st.column_config.TextColumn("ID", width="small"),
            "Ism": st.column_config.TextColumn("Ism", width="medium"),
            "Familiya": st.column_config.TextColumn("Familiya", width="medium"),
            "Yosh": st.column_config.NumberColumn("Yosh", width="small"),
            "O'quv joyi": st.column_config.TextColumn("O'quv joyi", width="large"),
            "Kategoriya": st.column_config.TextColumn("Kategoriya", width="medium"),
            "Telefon": st.column_config.TextColumn("Telefon", width="medium"),
            "Tarif": st.column_config.TextColumn("Tarif", width="small"),
        }
    )

    # Excel yuklab olish
    col1, col2 = st.columns([1, 5])
    with col1:
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 Excel yuklab olish",
            data=csv,
            file_name=f"kutubxona_users_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

else:
    st.info("Hozircha foydalanuvchilar yo'q")

st.markdown("---")

# O'quv joylari batafsil ro'yxati
st.header("🏛️ O'quv Joylari Ro'yxati")

with st.expander("📋 Batafsil ko'rish"):
    if all_users:
        # Barcha o'quv joylarni olish
        study_places = {}
        for user in all_users:
            if user.study_place and user.study_place != "Kiritilmagan":
                category = categorize_study_place(user.study_place)
                if category not in study_places:
                    study_places[category] = []
                study_places[category].append(user.study_place)

        # Kategoriya bo'yicha ko'rsatish
        for category, places in sorted(study_places.items()):
            st.subheader(category)
            place_counts = Counter(places)
            place_df = pd.DataFrame({
                "O'quv joyi": list(place_counts.keys()),
                "Foydalanuvchilar soni": list(place_counts.values())
            }).sort_values("Foydalanuvchilar soni", ascending=False)

            st.dataframe(place_df, use_container_width=True)

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
            "O'quv joyi": user.study_place,
            "Telefon": user.phone_number,
            "Tarif": user.subscription_plan,
            "Qolgan kunlar": days_left,
            "Tugash sanasi": user.subscription_end_date.strftime("%d.%m.%Y")
        })

    warning_df = pd.DataFrame(warning_data)
    st.dataframe(warning_df, use_container_width=True)

    # Ogohlantirish yuborish tugmasi
    if st.button("📨 Barcha foydalanuvchilarga ogohlantirish yuborish"):
        st.info("⏳ Bu funksiya ishlab chiqilmoqda...")
else:
    st.success("✅ Ogohlantirish kerak bo'lgan foydalanuvchilar yo'q")

st.markdown("---")

# Tezkor statistika
st.header("⚡ Tezkor Statistika")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("📅 Bugun")
    today_count = len([u for u in all_users if u.created_at and
                       u.created_at.date() == datetime.now().date()])
    st.metric("Yangi foydalanuvchilar", today_count)

with col2:
    st.subheader("📆 Bu hafta")
    week_ago = datetime.now() - timedelta(days=7)
    week_count = len([u for u in all_users if u.created_at and
                      u.created_at >= week_ago])
    st.metric("Yangi foydalanuvchilar", week_count)

with col3:
    st.subheader("📊 Bu oy")
    month_ago = datetime.now() - timedelta(days=30)
    month_count = len([u for u in all_users if u.created_at and
                       u.created_at >= month_ago])
    st.metric("Yangi foydalanuvchilar", month_count)

# Database yopish
db.close()

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
        📚 Kutubxona Boshqaruv Tizimi | Versiya 2.0 | Ishlab chiqilgan: 2025
    </div>
    """,
    unsafe_allow_html=True
)