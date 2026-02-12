import streamlit as st
from database import init_database
from utils import load_css
from init_db import create_placeholder_image, init_sample_data

# ✅ เปลี่ยนจาก import show มา import ทั้งโมดูล
import pages.view_items as view_items
import pages.manage_items as manage_items
import pages.admin as admin

st.set_page_config(
    page_title="Item Wiki - ARPG",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_css()

if 'initialized' not in st.session_state:
    init_database()
    create_placeholder_image()
    init_sample_data()
    st.session_state.initialized = True

# ✅ เมนู Sidebar
with st.sidebar:
    st.markdown("## 🎮 ITEM WIKI")
    st.markdown("---")

    menu = st.radio(
        "เมนู",
        ["🏠 หน้าหลัก", "🔍 ค้นหาไอเท็ม", "📝 จัดการไอเท็ม", "⚙️ ADMIN"],
        label_visibility="collapsed"
    )

    st.markdown("---")

    # แสดงสถิติด้านข้าง
    from database import execute_query

    count = execute_query("SELECT COUNT(*) as count FROM items WHERE name NOT LIKE '[%]%'")
    total_items = count[0]['count'] if count else 0
    st.markdown(f"**📊 ไอเท็ม:** {total_items} ชิ้น")

# ✅ หน้าหลัก
if menu == "🏠 หน้าหลัก":
    col1, col2 = st.columns([1, 5])
    with col1:
        st.markdown("# 🎮")
    with col2:
        st.markdown("# Item Wiki สำหรับเกม ARPG")
        st.markdown("ฐานข้อมูลไอเท็มสำหรับนักผจญภัย")

    st.markdown("---")
    st.markdown("""
    ## 📋 ยินดีต้อนรับ

    ระบบฐานข้อมูลไอเท็มสำหรับเกม ARPG รองรับการค้นหา เพิ่ม แก้ไข และลบไอเท็ม

    ### ✨ ความสามารถหลัก:
    - 🔍 **ค้นหาไอเท็ม** - ค้นหาชื่อไอเท็ม, กรองตามประเภท, ความหายาก, สถานที่ดรอป, Tier
    - 📝 **จัดการไอเท็ม** - เพิ่ม, แก้ไข, ลบไอเท็ม พร้อมอัปโหลดรูปภาพ
    - 🗑️ **ลบหลายรายการ** - เลือกลบทีละหลายชิ้น หรือลบทั้งหมด
    - ⚙️ **ADMIN** - จัดการข้อมูลหลัก (ประเภท, ความหายาก, สถานที่ดรอป, Tier)

    ### 📊 สถิติ
    """)

    from database import execute_query

    count = execute_query("SELECT COUNT(*) as count FROM items WHERE name NOT LIKE '[%]%'")[0]['count']
    legendary = \
    execute_query("SELECT COUNT(*) as count FROM items WHERE rarity = 'Legendary' AND name NOT LIKE '[%]%'")[0]['count']
    epic = execute_query("SELECT COUNT(*) as count FROM items WHERE rarity = 'Epic' AND name NOT LIKE '[%]%'")[0][
        'count']

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("ไอเท็มทั้งหมด", f"{count} ชิ้น")
    with col2:
        st.metric("Legendary", f"{legendary} ชิ้น")
    with col3:
        st.metric("Epic", f"{epic} ชิ้น")

    st.markdown("---")
    st.caption("👈 เลือกเมนูจาก Sidebar เพื่อเริ่มใช้งาน")

# ✅ เรียกหน้าที่เลือก
elif menu == "🔍 ค้นหาไอเท็ม":
    view_items.show()
elif menu == "📝 จัดการไอเท็ม":
    manage_items.show()
elif menu == "⚙️ ADMIN":
    admin.show()