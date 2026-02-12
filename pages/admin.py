import streamlit as st
from database import get_master_data, add_master_data, delete_master_data, update_master_data_color
from utils import get_item_types, get_rarities, get_drop_locations, get_tiers
from database import execute_query


def manage_types():
    st.markdown("### 📦 จัดการประเภทไอเท็ม")

    col1, col2 = st.columns([2, 1])

    with col2:
        st.markdown("**➕ เพิ่มประเภทใหม่**")
        with st.form("add_type_form"):
            new_type = st.text_input("ชื่อประเภท", placeholder="เช่น อาวุธ, เกราะ, เครื่องประดับ")
            submitted = st.form_submit_button("💾 เพิ่ม", use_container_width=True)

            if submitted and new_type:
                if add_master_data('type', new_type):
                    st.success(f"✅ เพิ่มประเภท '{new_type}' เรียบร้อย!")
                    st.rerun()
                else:
                    st.error(f"⚠️ ประเภท '{new_type}' มีอยู่แล้ว!")

    with col1:
        types = get_item_types()
        if types:
            for t in types:
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    count = execute_query("SELECT COUNT(*) as c FROM items WHERE type = ?", (t,), fetch_one=True)
                    item_count = count['c'] if count else 0
                    st.markdown(f"• **{t}** {f'({item_count} ชิ้น)' if item_count > 0 else ''}")

                with col_b:
                    if st.button("🗑️", key=f"del_type_{t}"):
                        if delete_master_data('type', t):
                            st.success(f"✅ ลบประเภท '{t}' เรียบร้อย!")
                            st.rerun()
                        else:
                            st.error(f"⚠️ ไม่สามารถลบได้: มีไอเท็ม {item_count} ชิ้นที่ใช้ประเภท '{t}'")
        else:
            st.info("ยังไม่มีประเภทไอเท็ม")


def manage_rarities():
    st.markdown("### ⭐ จัดการความหายาก")

    col1, col2 = st.columns([2, 1])

    with col2:
        st.markdown("**➕ เพิ่มความหายากใหม่**")
        with st.form("add_rarity_form"):
            new_rarity = st.text_input("ชื่อความหายาก", placeholder="เช่น Common, Rare, Legendary")
            new_color = st.color_picker("สีที่ใช้แสดง", value="#808080")
            submitted = st.form_submit_button("💾 เพิ่ม", use_container_width=True)

            if submitted and new_rarity:
                if add_master_data('rarity', new_rarity, new_color):
                    st.success(f"✅ เพิ่มความหายาก '{new_rarity}' เรียบร้อย!")
                    st.rerun()
                else:
                    st.error(f"⚠️ ความหายาก '{new_rarity}' มีอยู่แล้ว!")

    with col1:
        rarities = get_rarities()
        if rarities:
            for r, color in rarities:
                col_a, col_b, col_c = st.columns([2, 1, 1])
                with col_a:
                    count = execute_query("SELECT COUNT(*) as c FROM items WHERE rarity = ?", (r,), fetch_one=True)
                    item_count = count['c'] if count else 0
                    st.markdown(
                        f"<span style='color:{color};'>• **{r}**</span> {f'({item_count} ชิ้น)' if item_count > 0 else ''}",
                        unsafe_allow_html=True)

                with col_b:
                    if st.button("🎨", key=f"edit_color_{r}"):
                        st.session_state[f"editing_color_{r}"] = True

                with col_c:
                    if st.button("🗑️", key=f"del_rarity_{r}"):
                        if delete_master_data('rarity', r):
                            st.success(f"✅ ลบความหายาก '{r}' เรียบร้อย!")
                            st.rerun()
                        else:
                            st.error(f"⚠️ ไม่สามารถลบได้: มีไอเท็ม {item_count} ชิ้นที่ใช้ความหายาก '{r}'")

                if st.session_state.get(f"editing_color_{r}", False):
                    with st.form(key=f"color_form_{r}"):
                        new_color = st.color_picker("เลือกสีใหม่", value=color)
                        col_s1, col_s2 = st.columns(2)
                        with col_s1:
                            if st.form_submit_button("💾 บันทึก"):
                                if update_master_data_color('rarity', r, new_color):
                                    st.success(f"✅ อัปเดตสี '{r}' เรียบร้อย!")
                                    st.session_state[f"editing_color_{r}"] = False
                                    st.rerun()
                        with col_s2:
                            if st.form_submit_button("❌ ยกเลิก"):
                                st.session_state[f"editing_color_{r}"] = False
                                st.rerun()
        else:
            st.info("ยังไม่มีข้อมูลความหายาก")


def manage_locations():
    st.markdown("### 📍 จัดการสถานที่ดรอป")

    col1, col2 = st.columns([2, 1])

    with col2:
        st.markdown("**➕ เพิ่มสถานที่ดรอปใหม่**")
        with st.form("add_location_form"):
            new_location = st.text_input("ชื่อสถานที่", placeholder="เช่น ดันเจี้ยนไฟ, ป่าลึกลับ")
            submitted = st.form_submit_button("💾 เพิ่ม", use_container_width=True)

            if submitted and new_location:
                if add_master_data('location', new_location):
                    st.success(f"✅ เพิ่มสถานที่ '{new_location}' เรียบร้อย!")
                    st.rerun()
                else:
                    st.error(f"⚠️ สถานที่ '{new_location}' มีอยู่แล้ว!")

    with col1:
        locations = get_drop_locations()
        if locations:
            for loc in locations:
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    count = execute_query("SELECT COUNT(*) as c FROM items WHERE drop_location = ?", (loc,),
                                          fetch_one=True)
                    item_count = count['c'] if count else 0
                    st.markdown(f"• **{loc}** {f'({item_count} ชิ้น)' if item_count > 0 else ''}")

                with col_b:
                    if st.button("🗑️", key=f"del_loc_{loc}"):
                        if delete_master_data('location', loc):
                            st.success(f"✅ ลบสถานที่ '{loc}' เรียบร้อย!")
                            st.rerun()
                        else:
                            st.error(f"⚠️ ไม่สามารถลบได้: มีไอเท็ม {item_count} ชิ้นที่ดรอปที่ '{loc}'")
        else:
            st.info("ยังไม่มีข้อมูลสถานที่ดรอป")


def manage_tiers():
    st.markdown("### 📊 จัดการ Tier")

    col1, col2 = st.columns([2, 1])

    with col2:
        st.markdown("**➕ เพิ่ม Tier ใหม่**")
        with st.form("add_tier_form"):
            new_tier = st.text_input("ชื่อ Tier", placeholder="เช่น T1, T2, T3, T4")
            submitted = st.form_submit_button("💾 เพิ่ม", use_container_width=True)

            if submitted and new_tier:
                if add_master_data('tier', new_tier):
                    st.success(f"✅ เพิ่ม Tier '{new_tier}' เรียบร้อย!")
                    st.rerun()
                else:
                    st.error(f"⚠️ Tier '{new_tier}' มีอยู่แล้ว!")

    with col1:
        tiers = get_tiers()
        if tiers:
            for t in tiers:
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    count = execute_query("SELECT COUNT(*) as c FROM items WHERE tier = ?", (t,), fetch_one=True)
                    item_count = count['c'] if count else 0
                    st.markdown(f"• **{t}** {f'({item_count} ชิ้น)' if item_count > 0 else ''}")

                with col_b:
                    if st.button("🗑️", key=f"del_tier_{t}"):
                        if delete_master_data('tier', t):
                            st.success(f"✅ ลบ Tier '{t}' เรียบร้อย!")
                            st.rerun()
                        else:
                            st.error(f"⚠️ ไม่สามารถลบได้: มีไอเท็ม {item_count} ชิ้นที่ใช้ Tier '{t}'")
        else:
            st.info("ยังไม่มีข้อมูล Tier")


def show():
    """หน้าหลัก ADMIN"""
    st.markdown("# ⚙️ ADMIN")
    st.markdown("### จัดการข้อมูลหลัก")
    st.markdown("---")

    tab1, tab2, tab3, tab4 = st.tabs([
        "📦 จัดการประเภทไอเท็ม",
        "⭐ จัดการความหายาก",
        "📍 จัดการสถานที่ดรอป",
        "📊 จัดการ Tier"
    ])

    with tab1:
        manage_types()

    with tab2:
        manage_rarities()

    with tab3:
        manage_locations()

    with tab4:
        manage_tiers()

    st.markdown("---")
    st.markdown("### 📊 สถิติข้อมูลหลัก")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("📦 ประเภท", len(get_item_types()))
    with col2:
        st.metric("⭐ ความหายาก", len(get_rarities()))
    with col3:
        st.metric("📍 สถานที่ดรอป", len(get_drop_locations()))
    with col4:
        st.metric("📊 Tier", len(get_tiers()))

    st.markdown("---")
    st.caption("""
    **หมายเหตุ:**
    - การเพิ่ม/แก้ไข/ลบข้อมูลจะถูกบันทึกในระบบทันที
    - ไม่สามารถลบข้อมูลที่มีไอเท็มใช้งานอยู่ได้
    - ข้อมูลที่เพิ่มจะแสดงในหน้าค้นหาและจัดการอัตโนมัติ
    """)