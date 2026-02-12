import streamlit as st
from database import execute_query, check_duplicate_name
from models import Item
from utils import validate_item_data, get_rarity_color
from utils import get_item_types, get_rarity_values, get_drop_locations, get_tiers
import os
from datetime import datetime


def add_item_form():
    if 'add_success_message' not in st.session_state:
        st.session_state.add_success_message = None

    if st.session_state.add_success_message:
        st.success(st.session_state.add_success_message)
        st.balloons()
        if st.button("➕ เพิ่มไอเท็มอีกชิ้น"):
            st.session_state.add_success_message = None
            st.rerun()
        st.markdown("---")

    with st.form("add_item_form"):
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input("ชื่อไอเท็ม*", placeholder="เช่น ดาบแห่งเพลิง")

            # ดึงประเภทจาก Master Data
            item_types = get_item_types()
            if not item_types:
                item_types = ["อาวุธ", "เกราะ", "เครื่องประดับ", "เครื่องราง", "อื่นๆ"]
            item_type = st.selectbox("ประเภทไอเท็ม*", item_types, key="add_type")

            # ดึงความหายากจาก Master Data
            rarities = get_rarity_values()
            if not rarities:
                rarities = ["Common", "Uncommon", "Rare", "Epic", "Legendary"]
            rarity = st.selectbox("ความหายาก*", rarities, key="add_rarity")

        with col2:
            # ดึงสถานที่ดรอปจาก Master Data
            locations = get_drop_locations()
            if not locations:
                locations = ["ดันเจี้ยนไฟ", "ป่าลึกลับ", "ยอดเขา", "ถ้ำแมงมุม", "รังมังกร"]
            drop_location = st.selectbox("สถานที่ดรอป*", locations, key="add_location")

            # ดึง Tier จาก Master Data
            tiers = get_tiers()
            if not tiers:
                tiers = ["T1", "T2", "T3", "T4"]
            tier = st.selectbox("Tier*", tiers, key="add_tier")

            image_file = st.file_uploader("รูปภาพไอเท็ม", type=['png', 'jpg', 'jpeg'], key="add_image")

        description = st.text_area("คำอธิบาย", placeholder="ระบุรายละเอียดของไอเท็ม...", height=100, key="add_desc")

        submitted = st.form_submit_button("💾 บันทึกไอเท็ม", use_container_width=True)

        if submitted:
            errors = validate_item_data(name, item_type, rarity, drop_location, tier)

            if errors:
                for error in errors:
                    st.error(error)
            else:
                if check_duplicate_name(name):
                    st.error(f"⚠️ ไอเท็มชื่อ '{name}' มีอยู่แล้ว!")
                else:
                    image_path = "assets/images/placeholder.png"
                    if image_file:
                        os.makedirs("assets/images", exist_ok=True)
                        file_name = f"{name}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
                        image_path = f"assets/images/{file_name}"
                        with open(image_path, "wb") as f:
                            f.write(image_file.getbuffer())

                    query = '''
                        INSERT INTO items (name, type, rarity, drop_location, tier, description, image_path)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    '''
                    execute_query(query,
                                  (name.strip(), item_type, rarity, drop_location, tier, description, image_path))
                    st.session_state.add_success_message = f"✅ เพิ่มไอเท็ม '{name}' เรียบร้อย!"
                    st.rerun()


def edit_item_form(item):
    if 'edit_success_message' not in st.session_state:
        st.session_state.edit_success_message = None

    if st.session_state.edit_success_message:
        st.success(st.session_state.edit_success_message)
        st.balloons()
        st.session_state.edit_success_message = None

    with st.form(f"edit_item_form_{item.id}"):
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input("ชื่อไอเท็ม*", value=item.name, key=f"edit_name_{item.id}")

            # ดึงประเภทจาก Master Data
            item_types = get_item_types()
            if not item_types:
                item_types = ["อาวุธ", "เกราะ", "เครื่องประดับ", "เครื่องราง", "อื่นๆ"]

            if item.type not in item_types and item.type not in ["SYSTEM"]:
                item_types.append(item.type)

            type_index = item_types.index(item.type) if item.type in item_types else 0
            item_type = st.selectbox("ประเภทไอเท็ม*", item_types, index=type_index, key=f"edit_type_{item.id}")

            # ดึงความหายากจาก Master Data
            rarities = get_rarity_values()
            if not rarities:
                rarities = ["Common", "Uncommon", "Rare", "Epic", "Legendary"]

            if item.rarity not in rarities and item.rarity not in ["SYSTEM"]:
                rarities.append(item.rarity)

            rarity_index = rarities.index(item.rarity) if item.rarity in rarities else 0
            rarity = st.selectbox("ความหายาก*", rarities, index=rarity_index, key=f"edit_rarity_{item.id}")

        with col2:
            # ดึงสถานที่ดรอปจาก Master Data
            locations = get_drop_locations()
            if not locations:
                locations = ["ดันเจี้ยนไฟ", "ป่าลึกลับ", "ยอดเขา", "ถ้ำแมงมุม", "รังมังกร"]

            if item.drop_location not in locations and item.drop_location not in ["SYSTEM"]:
                locations.append(item.drop_location)

            location_index = locations.index(item.drop_location) if item.drop_location in locations else 0
            drop_location = st.selectbox("สถานที่ดรอป*", locations, index=location_index,
                                         key=f"edit_location_{item.id}")

            # ดึง Tier จาก Master Data
            tiers = get_tiers()
            if not tiers:
                tiers = ["T1", "T2", "T3", "T4"]

            if item.tier not in tiers and item.tier not in ["SYSTEM"]:
                tiers.append(item.tier)

            tier_index = tiers.index(item.tier) if item.tier in tiers else 0
            tier = st.selectbox("Tier*", tiers, index=tier_index, key=f"edit_tier_{item.id}")

            if item.image_path and item.image_path != "assets/images/placeholder.png":
                try:
                    from PIL import Image
                    img = Image.open(item.image_path)
                    st.image(img, width=100, caption="รูปปัจจุบัน")
                except:
                    pass

            image_file = st.file_uploader("เปลี่ยนรูปภาพ", type=['png', 'jpg', 'jpeg'], key=f"edit_image_{item.id}")

        description = st.text_area("คำอธิบาย", value=item.description, height=100, key=f"edit_desc_{item.id}")

        col1, col2, col3 = st.columns(3)
        with col1:
            update_btn = st.form_submit_button("💾 อัปเดต", use_container_width=True)
        with col2:
            delete_btn = st.form_submit_button("🗑️ ลบ", use_container_width=True)
        with col3:
            cancel_btn = st.form_submit_button("↩️ ยกเลิก", use_container_width=True)

        if update_btn:
            errors = validate_item_data(name, item_type, rarity, drop_location, tier)

            if errors:
                for error in errors:
                    st.error(error)
            else:
                if name.strip() != item.name and check_duplicate_name(name, exclude_id=item.id):
                    st.error(f"⚠️ ไอเท็มชื่อ '{name}' มีอยู่แล้ว!")
                else:
                    image_path = item.image_path
                    if image_file:
                        os.makedirs("assets/images", exist_ok=True)
                        file_name = f"{name}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
                        image_path = f"assets/images/{file_name}"
                        with open(image_path, "wb") as f:
                            f.write(image_file.getbuffer())

                    query = '''
                        UPDATE items 
                        SET name = ?, type = ?, rarity = ?, drop_location = ?, 
                            tier = ?, description = ?, image_path = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                    '''
                    execute_query(query, (name.strip(), item_type, rarity, drop_location, tier, description, image_path,
                                          item.id))
                    st.session_state.edit_success_message = f"✅ อัปเดต '{name}' เรียบร้อย!"
                    st.rerun()

        if delete_btn:
            st.warning(f"ต้องการลบ '{item.name}'?")
            confirm = st.checkbox("✓ ยืนยันการลบ", key=f"confirm_del_{item.id}")
            if confirm:
                execute_query("DELETE FROM items WHERE id = ?", (item.id,))
                st.success(f"🗑️ ลบ '{item.name}' เรียบร้อย!")
                st.balloons()
                st.rerun()

        if cancel_btn:
            st.rerun()


def manage_items_list():
    items = execute_query("SELECT * FROM items WHERE name NOT LIKE '[%]%' ORDER BY name")

    if not items:
        st.info("ℹ️ ยังไม่มีไอเท็มในระบบ")
        return

    item_options = {f"{item['name']} ({item['rarity']})": item['id'] for item in items}
    selected_display = st.selectbox("เลือกไอเท็มที่ต้องการแก้ไข", list(item_options.keys()), key="select_edit_item")

    if selected_display:
        selected_id = item_options[selected_display]
        item_data = execute_query("SELECT * FROM items WHERE id = ?", (selected_id,), fetch_one=True)

        if item_data:
            item = Item.from_dict(dict(item_data))
            edit_item_form(item)


def bulk_delete_items():
    st.markdown("### 🗑️ ลบหลายรายการ")

    items = execute_query("SELECT * FROM items WHERE name NOT LIKE '[%]%' ORDER BY name")

    if not items:
        st.info("ℹ️ ยังไม่มีไอเท็ม")
        return

    total = len(items)
    st.metric("ไอเท็มทั้งหมด", f"{total} ชิ้น")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ เลือกทั้งหมด", use_container_width=True):
            for item in items:
                st.session_state[f"bulk_del_{item['id']}"] = True
            st.rerun()
    with col2:
        if st.button("❌ ยกเลิกทั้งหมด", use_container_width=True):
            for item in items:
                if f"bulk_del_{item['id']}" in st.session_state:
                    del st.session_state[f"bulk_del_{item['id']}"]
            st.rerun()

    cols = st.columns(3)
    selected = []

    for idx, item in enumerate(items):
        with cols[idx % 3]:
            if st.checkbox(f"{item['name']}", key=f"bulk_del_{item['id']}"):
                selected.append(item['id'])
                st.markdown(f"<small style='color:{get_rarity_color(item['rarity'])};'>{item['rarity']}</small>",
                            unsafe_allow_html=True)

    if selected:
        st.warning(f"เลือก {len(selected)} รายการ")

        if st.button(f"🗑️ ลบ {len(selected)} รายการ", type="primary", use_container_width=True):
            if 'confirm_bulk_delete' not in st.session_state:
                st.session_state.confirm_bulk_delete = True
                st.warning("⚠️ กดยืนยันอีกครั้ง!")
                st.rerun()
            else:
                placeholders = ','.join(['?'] * len(selected))
                execute_query(f"DELETE FROM items WHERE id IN ({placeholders})", selected)
                st.session_state.pop('confirm_bulk_delete', None)
                for item_id in selected:
                    if f"bulk_del_{item_id}" in st.session_state:
                        st.session_state.pop(f"bulk_del_{item_id}", None)
                st.success(f"✅ ลบ {len(selected)} รายการเรียบร้อย!")
                st.balloons()
                st.rerun()

    st.markdown("---")
    st.markdown("#### ⚠️ ลบทั้งหมด")

    col1, col2 = st.columns([1, 3])
    with col1:
        delete_all_confirm = st.checkbox("ฉันต้องการลบทั้งหมด", key="delete_all_confirm")

    if delete_all_confirm:
        if st.button("🗑️ ลบทั้งหมด", use_container_width=True):
            if 'confirm_delete_all' not in st.session_state:
                st.session_state.confirm_delete_all = True
                st.error("⚠️⚠️ กดยืนยันอีกครั้ง!")
                st.rerun()
            else:
                execute_query("DELETE FROM items WHERE name NOT LIKE '[%]%'")
                st.session_state.pop('confirm_delete_all', None)
                st.session_state['delete_all_confirm'] = False
                st.success(f"✅ ลบทั้งหมด {total} รายการ!")
                st.balloons()
                st.rerun()


def show():
    """หน้าหลัก MANAGE ITEMS"""
    st.markdown("# 📝 MANAGE ITEMS")

    tab1, tab2, tab3 = st.tabs(["➕ เพิ่มไอเท็มใหม่", "✏️ แก้ไข/ลบไอเท็ม", "🗑️ ลบหลายรายการ"])

    with tab1:
        add_item_form()

    with tab2:
        manage_items_list()

    with tab3:
        bulk_delete_items()