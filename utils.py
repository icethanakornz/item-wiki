import os
import base64
from PIL import Image
import streamlit as st
from database import execute_query, get_master_data

def load_css():
    st.markdown("""
        <style>
        .stApp {
            background-color: #0E1117;
            color: #FAFAFA;
        }
        .css-1d391kg {
            background-color: #1E1E1E;
        }
        .item-card {
            background-color: #262730;
            border-radius: 10px;
            padding: 20px;
            margin: 10px 0;
            border-left: 5px solid;
            transition: transform 0.3s;
        }
        .item-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        }
        .rarity-common { border-left-color: #808080; }
        .rarity-uncommon { border-left-color: #27ae60; }
        .rarity-rare { border-left-color: #2980b9; }
        .rarity-epic { border-left-color: #8e44ad; }
        .rarity-legendary { border-left-color: #f39c12; }
        .stButton button {
            background-color: #3498db;
            color: white;
            border-radius: 5px;
        }
        .stButton button:hover {
            background-color: #2980b9;
        }
        .stTextInput input {
            background-color: #262730;
            color: white;
            border: 1px solid #4A4A4A;
        }
        </style>
    """, unsafe_allow_html=True)

def get_image_base64(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return None

def validate_item_data(name, type_, rarity, drop_location, tier):
    errors = []
    if not name or len(name.strip()) == 0:
        errors.append("กรุณาระบุชื่อไอเท็ม")
    if not type_:
        errors.append("กรุณาเลือกประเภทไอเท็ม")
    if not rarity:
        errors.append("กรุณาเลือกความหายาก")
    if not drop_location:
        errors.append("กรุณาระบุสถานที่ดรอป")
    if not tier:
        errors.append("กรุณาเลือก Tier")
    return errors

# ===== ฟังก์ชันดึงข้อมูลจาก Master Data =====

def get_item_types():
    """ดึงรายการประเภทไอเท็มจาก master_data"""
    data = get_master_data('type')
    return [row['value'] for row in data] if data else []

def get_rarities():
    """ดึงรายการความหายากจาก master_data พร้อมสี"""
    data = get_master_data('rarity')
    if data:
        return [(row['value'], row['color']) for row in data]
    return []

def get_rarity_values():
    """ดึงเฉพาะค่าความหายาก"""
    return [r[0] for r in get_rarities()]

def get_drop_locations():
    """ดึงรายการสถานที่ดรอปจาก master_data"""
    data = get_master_data('location')
    return [row['value'] for row in data] if data else []

def get_tiers():
    """ดึงรายการ Tier จาก master_data"""
    data = get_master_data('tier')
    return [row['value'] for row in data] if data else []

def get_filter_options():
    """ดึงข้อมูลสำหรับหน้า VIEW ITEMS"""
    return get_item_types(), get_rarity_values(), get_drop_locations(), get_tiers()

def get_rarity_color(rarity):
    """ดึงสีของความหายาก"""
    rarities = get_rarities()
    for r, color in rarities:
        if r == rarity:
            return color
    return "#808080"

def get_rarity_icon(rarity):
    icons = {
        "Common": "⚪",
        "Uncommon": "🟢",
        "Rare": "🔵",
        "Epic": "🟣",
        "Legendary": "🟡"
    }
    return icons.get(rarity, "⚪")
