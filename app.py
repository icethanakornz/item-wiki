import streamlit as st
from database import init_database
from utils import load_css
from init_db import create_placeholder_image, init_sample_data

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

# หน้าหลัก
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

### 📊 สถิติ
""")

from database import execute_query
count = execute_query("SELECT COUNT(*) as count FROM items")[0]['count']
legendary = execute_query("SELECT COUNT(*) as count FROM items WHERE rarity = 'Legendary'")[0]['count']
epic = execute_query("SELECT COUNT(*) as count FROM items WHERE rarity = 'Epic'")[0]['count']

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("ไอเท็มทั้งหมด", f"{count} ชิ้น")
with col2:
    st.metric("Legendary", f"{legendary} ชิ้น")
with col3:
    st.metric("Epic", f"{epic} ชิ้น")

st.markdown("---")
st.caption("👈 เลือกเมนูจาก Sidebar เพื่อเริ่มใช้งาน")