import streamlit as st
from database import execute_query, check_duplicate_name
from models import Item
from utils import validate_item_data, get_rarity_color
from utils import get_item_types, get_rarity_values, get_drop_locations, get_tiers
import os
from datetime import datetime
import pandas as pd
import io
import chardet  # เพิ่มสำหรับตรวจจับ encoding


# ===== ฟังก์ชัน Import CSV (แก้ไขให้รองรับ Excel) =====
def import_csv_form():
    st.markdown("### 📥 นำเข้าข้อมูลจาก CSV")
    st.markdown("---")

    st.info("""
    **รูปแบบไฟล์ CSV ที่รองรับ:**
    - ต้องมีคอลัมน์: `name, type, rarity, drop_location, tier, description`
    - ✅ Notepad / Text Editor (UTF-8)
    - ✅ Excel (บันทึกเป็น CSV UTF-8)
    - ⚠️ Excel บันทึกปกติ → ระบบจะแปลงให้อัตโนมัติ
    """)

    uploaded_file = st.file_uploader(
        "เลือกไฟล์ CSV",
        type=['csv'],
        key="csv_uploader",
        help="รองรับไฟล์จาก Excel และ Notepad"
    )

    if uploaded_file is not None:
        try:
            # อ่าน raw bytes
            raw_data = uploaded_file.read()

            # ตรวจจับ encoding อัตโนมัติ
            detected = chardet.detect(raw_data)
            encoding = detected['encoding']

            # ลองอ่านด้วย encoding ต่างๆ
            df = None
            errors = []

            # ลิสต์ encoding ที่ต้องลอง
            encodings_to_try = [
                encoding,  # ค่าที่ตรวจจับได้
                'utf-8-sig',  # Excel UTF-8 with BOM
                'utf-8',  # UTF-8 ปกติ
                'cp874',  # Windows Thai
                'windows-874',  # Windows Thai
                'tis-620',  # TIS-620
                'latin-1',  # Windows default
                'cp1252',  # Windows Western
                'ansi'  # ANSI
            ]

            # ลองอ่านทีละ encoding
            for enc in encodings_to_try:
                if enc is None:
                    continue
                try:
                    # รีเซ็ต pointer
                    uploaded_file.seek(0)
                    df = pd.read_csv(uploaded_file, encoding=enc)
                    st.success(f"✅ อ่านไฟล์สำเร็จด้วย encoding: {enc}")
                    break
                except:
                    errors.append(f"{enc} ❌")
                    continue

            # ถ้าอ่านไม่สำเร็จ ให้ลองอ่านแบบไม่ระบุ encoding
            if df is None:
                uploaded_file.seek(0)
                try:
                    df = pd.read_csv(uploaded_file)
                    st.success(f"✅ อ่านไฟล์สำเร็จ (auto-detect)")
                except Exception as e:
                    st.error(f"❌ ไม่สามารถอ่านไฟล์ CSV ได้: {str(e)}")
                    return

            # ลบช่องว่างหัวท้ายของชื่อคอลัมน์
            df.columns = df.columns.str.strip()

            # ตรวจสอบคอลัมน์ที่จำเป็น
            required_columns = ['name', 'type', 'rarity', 'drop_location', 'tier', 'description']
            missing_columns = [col for col in required_columns if col not in df.columns]

            if missing_columns:
                st.error(f"❌ ไฟล์ CSV ต้องมีคอลัมน์: {', '.join(missing_columns)}")
                st.info(f"📋 คอลัมน์ที่พบในไฟล์: {', '.join(df.columns)}")
                return

            # ลบข้อมูลว่าง
            df = df.dropna(subset=['name'], how='all')

            if len(df) == 0:
                st.error("❌ ไม่พบข้อมูลในไฟล์ CSV")
                return

            # แสดงตัวอย่างข้อมูล
            st.success(f"✅ อ่านไฟล์สำเร็จ! พบ {len(df)} รายการ")

            # แสดงตัวอย่างข้อมูล
            with st.expander("👁️ ดูตัวอย่างข้อมูล", expanded=False):
                # จัดรูปแบบข้อมูลให้อ่านง่าย
                preview_df = df[required_columns].head(10).copy()
                st.dataframe(preview_df, use_container_width=True)

            # แสดงสถิติ
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📊 รายการทั้งหมด", len(df))
            with col2:
                st.metric("📋 คอลัมน์", len(df.columns))
            with col3:
                st.metric("🔤 Encoding", encoding or 'auto')
            with col4:
                st.metric("📁 ไฟล์",
                          uploaded_file.name[:20] + '...' if len(uploaded_file.name) > 20 else uploaded_file.name)

            # ตัวเลือก
            st.markdown("---")
            st.markdown("### ⚙️ ตัวเลือกการนำเข้า")

            col1, col2 = st.columns(2)
            with col1:
                skip_duplicate = st.checkbox("ข้ามรายการที่ชื่อซ้ำ", value=True, key="skip_duplicate")
            with col2:
                preview_only = st.checkbox("แสดงตัวอย่างอย่างเดียว (ไม่บันทึก)", value=False, key="preview_only")

            # แสดงตัวอย่างการแมปข้อมูล
            with st.expander("🔍 ตรวจสอบข้อมูลก่อนนำเข้า", expanded=True):
                # แสดงสถิติแต่ละคอลัมน์
                col1, col2, col3 = st.columns(3)
                with col1:
                    unique_names = df['name'].nunique()
                    st.metric("ชื่อไอเท็ม", f"{len(df)} รายการ", f"{unique_names} ชื่อไม่ซ้ำ")
                with col2:
                    unique_types = df['type'].nunique()
                    st.metric("ประเภท", f"{unique_types} แบบ")
                with col3:
                    unique_rarities = df['rarity'].nunique()
                    st.metric("ความหายาก", f"{unique_rarities} แบบ")

            # ปุ่มนำเข้า
            if st.button("📥 ยืนยันการนำเข้า", type="primary", use_container_width=True):
                if preview_only:
                    st.success("✅ โหมดแสดงตัวอย่าง - ไม่มีการบันทึกข้อมูล")
                else:
                    # นำเข้าข้อมูล
                    success_count = 0
                    skip_count = 0
                    error_count = 0
                    error_details = []
                    duplicate_names = []

                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    for index, row in df.iterrows():
                        try:
                            progress = (index + 1) / len(df)
                            progress_bar.progress(progress)
                            status_text.text(f"กำลังนำเข้า: {index + 1}/{len(df)}")

                            # เอาช่องว่างออก
                            name = str(row['name']).strip()
                            item_type = str(row['type']).strip()
                            rarity = str(row['rarity']).strip()
                            drop_location = str(row['drop_location']).strip()
                            tier = str(row['tier']).strip()
                            description = str(row['description']).strip() if pd.notna(row['description']) else ""

                            # ข้ามข้อมูลว่าง
                            if not name or name == 'nan' or name == '':
                                skip_count += 1
                                continue

                            # ตรวจสอบข้อมูล
                            errors_list = validate_item_data(name, item_type, rarity, drop_location, tier)
                            if errors_list:
                                error_count += 1
                                error_details.append(f"แถว {index + 2}: {name} - {', '.join(errors_list)}")
                                continue

                            # ตรวจสอบชื่อซ้ำ
                            if skip_duplicate and check_duplicate_name(name):
                                skip_count += 1
                                duplicate_names.append(name)
                                continue

                            # บันทึกข้อมูล
                            query = '''
                                INSERT INTO items (name, type, rarity, drop_location, tier, description, image_path)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                            '''
                            execute_query(query, (
                                name,
                                item_type,
                                rarity,
                                drop_location,
                                tier,
                                description,
                                "assets/images/placeholder.png"
                            ))
                            success_count += 1

                        except Exception as e:
                            error_count += 1
                            error_details.append(
                                f"แถว {index + 2}: {name if 'name' in locals() else 'unknown'} - {str(e)}")

                    progress_bar.empty()
                    status_text.empty()

                    # แสดงผลลัพธ์
                    st.markdown("---")
                    st.markdown("### ✅ ผลการนำเข้า")

                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("✅ นำเข้าสำเร็จ", success_count)
                    with col2:
                        st.metric("⏭️ ข้ามรายการ", skip_count)
                    with col3:
                        st.metric("❌ ผิดพลาด", error_count)
                    with col4:
                        st.metric("📊 คงเหลือ", len(df) - success_count - skip_count - error_count)

                    if success_count > 0:
                        st.balloons()
                        st.success(f"✅ นำเข้าข้อมูลสำเร็จ {success_count} รายการ!")

                    # แสดงรายการชื่อที่ถูกข้าม
                    if duplicate_names:
                        with st.expander(f"⏭️ รายการที่ข้าม (ชื่อซ้ำ) {len(duplicate_names)} รายการ"):
                            st.write(", ".join(duplicate_names[:20]))
                            if len(duplicate_names) > 20:
                                st.write(f"... และอื่นๆ อีก {len(duplicate_names) - 20} รายการ")

                    # แสดงข้อผิดพลาด
                    if error_details:
                        with st.expander(f"❌ รายละเอียดข้อผิดพลาด {len(error_details)} รายการ"):
                            for err in error_details[:10]:
                                st.error(err)
                            if len(error_details) > 10:
                                st.warning(f"... และอื่นๆ อีก {len(error_details) - 10} รายการ")

                    if st.button("🔄 รีเฟรชหน้า"):
                        st.rerun()

        except Exception as e:
            st.error(f"❌ เกิดข้อผิดพลาด: {str(e)}")
            st.info("""
            💡 **วิธีการบันทึก CSV จาก Excel ที่ถูกต้อง:**

            1. **วิธีที่ 1 (แนะนำ):** บันทึกเป็น CSV UTF-8
               - File → Save As
               - เลือก "CSV UTF-8 (Comma delimited) (*.csv)"

            2. **วิธีที่ 2:** บันทึกแล้วให้ระบบแปลงให้
               - บันทึกเป็น CSV ปกติ
               - ระบบจะแปลง encoding ให้อัตโนมัติ

            3. **วิธีที่ 3:** ใช้ Notepad แก้ไข
               - เปิดไฟล์ CSV ด้วย Notepad
               - File → Save As
               - เลือก Encoding: UTF-8
            """)


# ===== ฟังก์ชันอื่นๆ คงเดิม =====
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
                        del st.session_state[f"bulk_del_{item_id}"]
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

    tab1, tab2, tab3, tab4 = st.tabs([
        "➕ เพิ่มไอเท็มใหม่",
        "✏️ แก้ไข/ลบไอเท็ม",
        "🗑️ ลบหลายรายการ",
        "📥 นำเข้า CSV"
    ])

    with tab1:
        add_item_form()

    with tab2:
        manage_items_list()

    with tab3:
        bulk_delete_items()

    with tab4:
        import_csv_form()