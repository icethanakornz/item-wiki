import streamlit as st
from database import execute_query
from models import Item
from utils import get_filter_options, get_image_base64, get_rarity_color, get_rarity_icon


def show_card_view(items_data):
    if not items_data:
        return

    cols = st.columns(3)
    for idx, item_data in enumerate(items_data):
        item = Item.from_dict(dict(item_data))
        with cols[idx % 3]:
            img_base64 = get_image_base64(item.image_path)
            if img_base64:
                st.markdown(f'<img src="data:image/png;base64,{img_base64}" style="width:100%; border-radius:10px;">',
                            unsafe_allow_html=True)

            rarity_class = f"rarity-{item.rarity.lower()}"
            st.markdown(f"""
            <div class="item-card {rarity_class}">
                <h3 style="color: white;">{item.name}</h3>
                <p style="color: #888;">{item.type} • {item.tier}</p>
                <p style="color: #ddd;">{item.description[:100]}{'...' if len(item.description) > 100 else ''}</p>
                <hr style="margin: 10px 0; border-color: #444;">
                <p style="color: #f39c12;">📍 {item.drop_location}</p>
                <p style="color: {get_rarity_color(item.rarity)};">
                    {get_rarity_icon(item.rarity)} {item.rarity}
                </p>
            </div>
            """, unsafe_allow_html=True)

            if st.button(f"ดูรายละเอียด", key=f"view_{item.id}"):
                show_item_detail(item)


def show_table_view(items_data):
    if not items_data:
        return

    table_data = []
    for item_data in items_data:
        item = Item.from_dict(dict(item_data))
        table_data.append({
            "ชื่อ": item.name,
            "ประเภท": item.type,
            "ความหายาก": item.rarity,
            "Tier": item.tier,
            "สถานที่ดรอป": item.drop_location,
            "รายละเอียด": item.description[:50] + "..." if len(item.description) > 50 else item.description,
        })
    st.dataframe(table_data, use_container_width=True, hide_index=True)


def show_item_detail(item):
    with st.expander(f"📖 รายละเอียด: {item.name}", expanded=True):
        col1, col2 = st.columns([1, 2])
        with col1:
            img_base64 = get_image_base64(item.image_path)
            if img_base64:
                st.markdown(f'<img src="data:image/png;base64,{img_base64}" style="width:100%; border-radius:10px;">',
                            unsafe_allow_html=True)
        with col2:
            st.markdown(f"### {item.name}")
            st.markdown(f"**ประเภท:** {item.type}")
            st.markdown(f"**ความหายาก:** {item.rarity}")
            st.markdown(f"**Tier:** {item.tier}")
            st.markdown(f"**สถานที่ดรอป:** {item.drop_location}")
            st.markdown("**คำอธิบาย:**")
            st.markdown(f">{item.description}")


def show():
    """หน้าหลัก VIEW ITEMS"""
    st.markdown("# 🔍 ค้นหาไอเท็ม")

    types, rarities, locations, tiers = get_filter_options()

    with st.sidebar:
        st.markdown("## 🎯 ตัวกรอง")
        selected_type = st.multiselect("ประเภทไอเท็ม", types, key="filter_type")
        selected_rarity = st.multiselect("ความหายาก", rarities, key="filter_rarity")
        selected_location = st.multiselect("สถานที่ดรอป", locations, key="filter_location")
        selected_tier = st.multiselect("Tier", tiers, key="filter_tier")

    search_query = st.text_input("🔎 ค้นหาชื่อไอเท็ม", placeholder="พิมพ์ชื่อไอเท็ม...")

    query = "SELECT * FROM items WHERE 1=1 AND name NOT LIKE '[%]%'"
    params = []

    if search_query:
        query += " AND name LIKE ?"
        params.append(f"%{search_query}%")

    if selected_type:
        placeholders = ','.join(['?'] * len(selected_type))
        query += f" AND type IN ({placeholders})"
        params.extend(selected_type)

    if selected_rarity:
        placeholders = ','.join(['?'] * len(selected_rarity))
        query += f" AND rarity IN ({placeholders})"
        params.extend(selected_rarity)

    if selected_location:
        placeholders = ','.join(['?'] * len(selected_location))
        query += f" AND drop_location IN ({placeholders})"
        params.extend(selected_location)

    if selected_tier:
        placeholders = ','.join(['?'] * len(selected_tier))
        query += f" AND tier IN ({placeholders})"
        params.extend(selected_tier)

    query += " ORDER BY name"

    items_data = execute_query(query, params)

    if not items_data:
        st.warning("😢 ไม่พบไอเท็มที่ค้นหา")
    else:
        st.success(f"พบ {len(items_data)} รายการ")

        view_mode = st.radio(
            "รูปแบบการแสดงผล",
            ["📱 การ์ด", "📊 ตาราง"],
            horizontal=True
        )

        if view_mode == "📊 ตาราง":
            show_table_view(items_data)
        else:
            show_card_view(items_data)