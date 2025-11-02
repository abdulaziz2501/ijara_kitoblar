"""
Kutubxona Dashboard - Streamlit
Yangilangan versiya - Library ID tizimi bilan
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
import os

# Database importini sozlash
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_manager import DatabaseManager
from database.admin_manager import AdminManager
from ijara_kitoblar.config import SUBSCRIPTION_PLANS

# Sahifa konfiguratsiyasi
st.set_page_config(
    page_title="Kutubxona Dashboard",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ========================================
# AUTENTIFIKATSIYA
# ========================================

def check_password():
    """Admin parolini tekshirish"""

    def password_entered():
        # O'zgartirilgan parol tizimi
        if st.session_state["password"] == "admin2025":  # O'zgartirishingiz mumkin
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.title("🔐 Dashboard Login")
        st.text_input(
            "Admin Paroli",
            type="password",
            on_change=password_entered,
            key="password"
        )
        st.info("💡 Default parol: admin2025")
        return False
    elif not st.session_state["password_correct"]:
        st.title("🔐 Dashboard Login")
        st.text_input(
            "Admin Paroli",
            type="password",
            on_change=password_entered,
            key="password"
        )
        st.error("❌ Noto'g'ri parol")
        return False
    else:
        return True


if not check_password():
    st.stop()

# ========================================
# CSS STILLARI
# ========================================

st.markdown("""
    <style>
    .main {
        padding: 1rem 2rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .warning-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
    }
    </style>
""", unsafe_allow_html=True)

# ========================================
# SARLAVHA
# ========================================

st.title("📚 Kutubxona Boshqaruv Tizimi v2.0")
st.markdown("*Library ID tizimi bilan yangilangan versiya*")
st.markdown("---")

# ========================================
# SIDEBAR
# ========================================

with st.sidebar:
    st.header("⚙️ Sozlamalar")

    # Refresh tugmasi
    if st.button("🔄 Yangilash", use_container_width=True):
        st.rerun()

    st.markdown("---")

    # Bo'lim tanlash
    page = st.radio(
        "📋 Bo'limlar",
        ["🏠 Dashboard", "👥 Foydalanuvchilar", "👨‍💼 Adminlar",
         "➕ Yangi Foydalanuvchi", "⚙️ Sozlamalar"]
    )

    st.markdown("---")

    # Vaqt
    st.markdown(f"🕐 {datetime.now().strftime('%d.%m.%Y %H:%M')}")

# ========================================
# DATABASE ULANISH
# ========================================

db = DatabaseManager()
admin_manager = AdminManager()

# ========================================
# DASHBOARD (Asosiy sahifa)
# ========================================

if page == "🏠 Dashboard":

    # Statistika
    st.header("📊 Asosiy Statistika")

    stats = db.get_statistics()
    admin_stats = admin_manager.get_admin_count()
    all_users = db.get_all_users()

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            label="👥 Jami Foydalanuvchilar",
            value=stats['total_users'],
            delta=f"+{len([u for u in all_users if (datetime.now() - u.created_at).days < 7])} (7 kun)"
        )

    with col2:
        st.metric(
            label="📗 Free",
            value=stats['free_users'],
            delta=f"{round(stats['free_users'] / stats['total_users'] * 100 if stats['total_users'] > 0 else 0)}%"
        )

    with col3:
        st.metric(
            label="📘 Money",
            value=stats['money_users'],
            delta=f"{round(stats['money_users'] / stats['total_users'] * 100 if stats['total_users'] > 0 else 0)}%"
        )

    with col4:
        st.metric(
            label="📕 Premium",
            value=stats['premium_users'],
            delta=f"{round(stats['premium_users'] / stats['total_users'] * 100 if stats['total_users'] > 0 else 0)}%"
        )

    with col5:
        st.metric(
            label="👨‍💼 Adminlar",
            value=admin_stats['total'],
            delta=f"Super: {admin_stats['super_admin']}"
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
            hole=.4,
            marker_colors=['#90EE90', '#87CEEB', '#FFB6C1'],
            textinfo='label+percent',
            textfont_size=14
        )])
        fig_plans.update_layout(
            title_text="Tariflar bo'yicha taqsimot",
            showlegend=True,
            height=400
        )
        st.plotly_chart(fig_plans, use_container_width=True)

    with col2:
        # Telegram bog'langan vs bog'lanmagan
        telegram_connected = stats['telegram_users']
        telegram_not_connected = stats['total_users'] - telegram_connected

        fig_telegram = go.Figure(data=[go.Bar(
            x=['Telegram Bog\'langan', 'Telegram Bog\'lanmagan'],
            y=[telegram_connected, telegram_not_connected],
            marker_color=['#4CAF50', '#FF9800'],
            text=[telegram_connected, telegram_not_connected],
            textposition='auto'
        )])
        fig_telegram.update_layout(
            title_text="Telegram Integratsiyasi",
            showlegend=False,
            height=400,
            yaxis_title="Foydalanuvchilar soni"
        )
        st.plotly_chart(fig_telegram, use_container_width=True)

    # Yosh guruhlari
    if all_users:
        st.subheader("📊 Yosh Guruhlari Taqsimoti")
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
            title="",
            color='Soni',
            color_continuous_scale='viridis'
        )
        fig_age.update_layout(height=350)
        st.plotly_chart(fig_age, use_container_width=True)

    st.markdown("---")

    # Ogohlantirish kerak bo'lganlar
    st.header("⚠️ Obunasi Tugaydigan Foydalanuvchilar (3 kun ichida)")

    warning_users = db.get_users_expiring_soon(warning_days=3)

    if warning_users:
        warning_data = []
        for user in warning_users:
            days_left = (user.subscription_end_date - datetime.now()).days
            warning_data.append({
                "🆔 Library ID": user.library_id,
                "👤 Ism": user.full_name,
                "📞 Telefon": user.phone_number,
                "📋 Tarif": user.subscription_plan,
                "⏰ Qolgan kunlar": days_left,
                "📅 Tugash sanasi": user.subscription_end_date.strftime("%d.%m.%Y"),
                "📱 Telegram": "✅" if user.telegram_id else "❌"
            })

        warning_df = pd.DataFrame(warning_data)
        st.dataframe(
            warning_df,
            use_container_width=True,
            height=min(len(warning_data) * 35 + 38, 400)
        )
    else:
        st.success("✅ Obunasi tugaydigan foydalanuvchilar yo'q")


# ========================================
# FOYDALANUVCHILAR SAHIFASI
# ========================================

elif page == "👥 Foydalanuvchilar":
    st.header("👥 Foydalanuvchilar Ro'yxati")

    all_users = db.get_all_users()

    if all_users:
        # Filtrlar
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            search_id = st.text_input("🔍 Library ID", placeholder="ID0001")

        with col2:
            search_name = st.text_input("🔍 Ism/Familiya", placeholder="Abdulloh")

        with col3:
            filter_plan = st.selectbox(
                "📋 Tarif",
                ["Barchasi", "Free", "Money", "Premium"]
            )

        with col4:
            filter_telegram = st.selectbox(
                "📱 Telegram",
                ["Barchasi", "Bog'langan", "Bog'lanmagan"]
            )

        # Ma'lumotlarni DataFrame ga aylantirish
        users_data = []
        for user in all_users:
            status = "✅" if user.is_active else "❌"
            telegram_status = "✅" if user.telegram_id else "❌"
            days_left = ""

            if user.subscription_end_date and user.subscription_plan != 'Free':
                days = (user.subscription_end_date - datetime.now()).days
                days_left = f"{days} kun" if days > 0 else "⚠️ Tugagan"

            users_data.append({
                "Status": status,
                "Library ID": user.library_id,
                "Ism": user.first_name,
                "Familiya": user.last_name,
                "Yosh": user.age,
                "Telefon": user.phone_number,
                "O'quv joyi": user.study_place,
                "Tarif": user.subscription_plan,
                "Qolgan muddat": days_left if days_left else "Cheksiz",
                "Telegram": telegram_status,
                "Ro'yxatdan o'tgan": user.created_at.strftime("%d.%m.%Y")
            })

        df = pd.DataFrame(users_data)

        # Filtrlash
        if search_id:
            df = df[df['Library ID'].str.contains(search_id, case=False, na=False)]

        if search_name:
            df = df[
                df['Ism'].str.contains(search_name, case=False, na=False) |
                df['Familiya'].str.contains(search_name, case=False, na=False)
                ]

        if filter_plan != "Barchasi":
            df = df[df['Tarif'] == filter_plan]

        if filter_telegram == "Bog'langan":
            df = df[df['Telegram'] == "✅"]
        elif filter_telegram == "Bog'lanmagan":
            df = df[df['Telegram'] == "❌"]

        # Natijalar soni
        st.info(f"📊 Jami: {len(df)} ta foydalanuvchi")

        # Jadvalni ko'rsatish
        st.dataframe(
            df,
            use_container_width=True,
            height=500,
            hide_index=True
        )

        # Export tugmalari
        col1, col2, col3 = st.columns(3)

        with col1:
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 CSV yuklab olish",
                data=csv,
                file_name=f"kutubxona_users_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )

        with col2:
            # Excel format
            excel_data = df.to_csv(index=False, sep='\t').encode('utf-8-sig')
            st.download_button(
                label="📊 Excel yuklab olish",
                data=excel_data,
                file_name=f"kutubxona_users_{datetime.now().strftime('%Y%m%d')}.xls",
                mime="application/vnd.ms-excel",
                use_container_width=True
            )

        st.markdown("---")

        # Tarif boshqaruvi
        st.subheader("⚙️ Tez Tarif Boshqaruvi")

        with st.expander("✏️ Foydalanuvchi tarifini o'zgartirish"):
            col1, col2, col3 = st.columns(3)

            with col1:
                user_id_to_update = st.selectbox(
                    "Foydalanuvchi",
                    options=[""] + [u.library_id for u in all_users],
                    format_func=lambda
                        x: x if x == "" else f"{x} - {next((u.full_name for u in all_users if u.library_id == x), '')}"
                )

            with col2:
                new_plan = st.selectbox("Yangi tarif", ["Free", "Money", "Premium"])

            with col3:
                st.write("")  # Spacing
                st.write("")  # Spacing
                update_btn = st.button("✅ Tarifni o'zgartirish", use_container_width=True)

            if update_btn and user_id_to_update:
                user = db.get_user_by_library_id(user_id_to_update)

                if user:
                    success, msg = db.update_subscription(user_id_to_update, new_plan)

                    if success:
                        st.success(
                            f"✅ {user.full_name} ({user_id_to_update}) "
                            f"ning tarifi {new_plan}ga o'zgartirildi!"
                        )
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")
                else:
                    st.error(f"❌ {user_id_to_update} ID raqamli foydalanuvchi topilmadi!")

    else:
        st.info("📂 Hozircha foydalanuvchilar yo'q")


# ========================================
# ADMINLAR SAHIFASI
# ========================================

elif page == "👨‍💼 Adminlar":
    st.header("👨‍💼 Adminlar Boshqaruvi")

    admins = admin_manager.get_all_admins()

    if admins:
        admin_data = []
        for admin in admins:
            admin_type = "⭐ SUPER ADMIN" if admin.is_super_admin else "👤 Admin"
            added_by_str = ""
            if admin.added_by:
                added_by_admin = admin_manager.get_admin_by_telegram_id(admin.added_by)
                if added_by_admin:
                    added_by_str = added_by_admin.full_name

            admin_data.append({
                "Tur": admin_type,
                "Library ID": admin.library_id,
                "Ism": admin.full_name,
                "Telegram ID": admin.telegram_id,
                "Qo'shilgan sana": admin.added_date.strftime("%d.%m.%Y"),
                "Qo'shgan": added_by_str if added_by_str else "Tizim"
            })

        admin_df = pd.DataFrame(admin_data)
        st.dataframe(admin_df, use_container_width=True, hide_index=True)

        st.info(f"📊 Jami: {len(admins)} ta admin")

    else:
        st.warning("⚠️ Adminlar topilmadi")


# ========================================
# YANGI FOYDALANUVCHI QO'SHISH
# ========================================

elif page == "➕ Yangi Foydalanuvchi":
    st.header("➕ Yangi Foydalanuvchi Qo'shish")
    st.info("💡 Bu foydalanuvchi to'g'ridan-to'g'ri kutubxonada ro'yxatdan o'tadi")

    with st.form("add_user_form"):
        col1, col2 = st.columns(2)

        with col1:
            first_name = st.text_input("Ism *", placeholder="Abdulloh")
            last_name = st.text_input("Familiya *", placeholder="Karimov")
            phone_number = st.text_input("Telefon *", placeholder="+998901234567")

        with col2:
            birth_year = st.number_input(
                "Tug'ilgan yil *",
                min_value=1940,
                max_value=datetime.now().year - 5,
                value=2000
            )
            study_place = st.text_input("O'quv joyi *", placeholder="Toshkent Davlat Universiteti")
            initial_plan = st.selectbox("Boshlang'ich tarif", ["Free", "Money", "Premium"])

        submitted = st.form_submit_button("✅ Foydalanuvchi qo'shish", use_container_width=True)

        if submitted:
            # Validatsiya
            if not all([first_name, last_name, phone_number, study_place]):
                st.error("❌ Barcha maydonlarni to'ldiring!")
            elif len(first_name) < 2 or len(last_name) < 2:
                st.error("❌ Ism va familiya kamida 2 ta harfdan iborat bo'lishi kerak!")
            else:
                # Telefon raqamni formatlash
                phone = phone_number.strip()
                if not phone.startswith('+'):
                    if phone.startswith('998'):
                        phone = '+' + phone
                    else:
                        phone = '+998' + phone.lstrip('0')

                # Foydalanuvchini yaratish
                user, error = db.create_user(
                    first_name=first_name.strip(),
                    last_name=last_name.strip(),
                    phone_number=phone,
                    birth_year=birth_year,
                    study_place=study_place.strip(),
                    telegram_id=None  # Dashboard dan qo'shilgan
                )

                if error:
                    st.error(f"❌ Xatolik: {error}")
                else:
                    # Tarifni o'rnatish
                    if initial_plan != "Free":
                        db.update_subscription(user.library_id, initial_plan)

                    st.success(
                        f"✅ MUVAFFAQIYATLI QO'SHILDI!\n\n"
                        f"📚 Library ID: **{user.library_id}**\n\n"
                        f"👤 {user.full_name}\n\n"
                        f"Bu ID ni foydalanuvchiga bering!"
                    )

                    st.balloons()


# ========================================
# SOZLAMALAR
# ========================================

elif page == "⚙️ Sozlamalar":
    st.header("⚙️ Sozlamalar va Ma'lumotlar")

    tab1, tab2, tab3 = st.tabs(["📊 Tariflar", "🔐 Xavfsizlik", "ℹ️ Tizim"])

    with tab1:
        st.subheader("💰 Tarif Rejalari")

        for plan_name, plan_info in SUBSCRIPTION_PLANS.items():
            with st.expander(f"{plan_name} - {plan_info['price']:,} so'm"):
                st.write(f"**Muddat:** {plan_info['duration_days']} kun")
                st.write("**Xususiyatlar:**")
                for feature in plan_info['features']:
                    st.write(f"• {feature}")

    with tab2:
        st.subheader("🔐 Xavfsizlik")
        st.info("🔒 Database: SQLite (Local)")
        st.info("📁 Database fayl: library.db")

        if st.button("💾 Database Backup yaratish"):
            import shutil

            backup_name = f"backup_library_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            try:
                shutil.copy('library.db', backup_name)
                st.success(f"✅ Backup yaratildi: {backup_name}")
            except Exception as e:
                st.error(f"❌ Xato: {e}")

    with tab3:
        st.subheader("ℹ️ Tizim Ma'lumotlari")
        st.write("**Versiya:** 2.0.0")
        st.write("**Yangilanish sanasi:** 2025-10-14")
        st.write("**Database:** SQLite")
        st.write("**Bot Framework:** Aiogram 3.13.1")
        st.write("**Dashboard:** Streamlit")

# ========================================
# DATABASE YOPISH
# ========================================

db.close()
admin_manager.close()

# ========================================
# FOOTER
# ========================================

st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray; padding: 1rem;'>
        📚 Kutubxona Boshqaruv Tizimi v2.0 | 
        Library ID tizimi | 
        © 2025
    </div>
    """,
    unsafe_allow_html=True
)