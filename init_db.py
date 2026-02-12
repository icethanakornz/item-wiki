import os
from database import init_database, execute_query
from PIL import Image, ImageDraw


def create_placeholder_image():
    os.makedirs("assets/images", exist_ok=True)
    img = Image.new('RGB', (200, 200), color=(73, 109, 137))
    d = ImageDraw.Draw(img)
    d.text((50, 90), "No Image", fill=(255, 255, 255))
    img.save('assets/images/placeholder.png')


def init_sample_data():
    # ตรวจสอบว่ามีข้อมูลตัวอย่างหรือยัง
    existing = execute_query("SELECT COUNT(*) as count FROM items")
    if existing and existing[0]['count'] == 0:
        sample_items = [
            {
                "name": "ดาบแห่งเพลิง",
                "type": "อาวุธ",
                "rarity": "Legendary",
                "drop_location": "ดันเจี้ยนไฟ",
                "tier": "T4",
                "description": "ดาบที่เต็มไปด้วยพลังแห่งเพลิง โอกาสติดสถานะเผาไหม้ 30%",
                "image_path": "assets/images/placeholder.png"
            },
            {
                "name": "เกราะน้ำแข็ง",
                "type": "เกราะ",
                "rarity": "Epic",
                "drop_location": "ยอดเขานิรันดร์",
                "tier": "T3",
                "description": "เกราะที่ทอจากน้ำแข็ง เพิ่มความต้านทานน้ำแข็ง 50%",
                "image_path": "assets/images/placeholder.png"
            },
            {
                "name": "แหวนแห่งโชค",
                "type": "เครื่องประดับ",
                "rarity": "Rare",
                "drop_location": "ป่าลึกลับ",
                "tier": "T2",
                "description": "เพิ่มอัตราคริติคอล 15% และโอกาสดรอปไอเทมหายาก",
                "image_path": "assets/images/placeholder.png"
            },
            {
                "name": "ธนูสายฟ้า",
                "type": "อาวุธ",
                "rarity": "Epic",
                "drop_location": "หอคอยสายฟ้า",
                "tier": "T3",
                "description": "ธนูที่ชาร์จด้วยพลังสายฟ้า กระสุนมีความเร็วสูง",
                "image_path": "assets/images/placeholder.png"
            },
            {
                "name": "รองเท้าจอมเวท",
                "type": "เกราะ",
                "rarity": "Uncommon",
                "drop_location": "หุบเขาเวทมนตร์",
                "tier": "T1",
                "description": "เพิ่มความเร็วเคลื่อนที่ 20% และฟื้นฟูมานา",
                "image_path": "assets/images/placeholder.png"
            },
            {
                "name": "คทามังกร",
                "type": "อาวุธ",
                "rarity": "Legendary",
                "drop_location": "รังมังกร",
                "tier": "T4",
                "description": "คทาที่ทำจากกระดูกมังกร เพิ่มพลังโจมตีเวท 100%",
                "image_path": "assets/images/placeholder.png"
            },
            {
                "name": "โล่แห่งความกล้า",
                "type": "เกราะ",
                "rarity": "Rare",
                "drop_location": "ป้อมปราการ",
                "tier": "T2",
                "description": "ลดความเสียหายจากการโจมตีระยะประชิด 30%",
                "image_path": "assets/images/placeholder.png"
            },
            {
                "name": "สร้อยไข่มุก",
                "type": "เครื่องประดับ",
                "rarity": "Common",
                "drop_location": "ชายหาด",
                "tier": "T1",
                "description": "เพิ่มพลังชีวิตสูงสุด 100",
                "image_path": "assets/images/placeholder.png"
            },
            {
                "name": "มีดสั้นพิษ",
                "type": "อาวุธ",
                "rarity": "Epic",
                "drop_location": "ถ้ำแมงมุม",
                "tier": "T3",
                "description": "โจมตีเร็ว โอกาสติดพิษ 40%",
                "image_path": "assets/images/placeholder.png"
            },
            {
                "name": "เข็มขัดยักษ์",
                "type": "เครื่องประดับ",
                "rarity": "Rare",
                "drop_location": "ดันเจี้ยนยักษ์",
                "tier": "T2",
                "description": "เพิ่มน้ำหนักที่ถือได้ 50 หน่วย",
                "image_path": "assets/images/placeholder.png"
            }
        ]

        for item_data in sample_items:
            query = '''
                INSERT INTO items (name, type, rarity, drop_location, tier, description, image_path)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            '''
            execute_query(query, (
                item_data['name'],
                item_data['type'],
                item_data['rarity'],
                item_data['drop_location'],
                item_data['tier'],
                item_data['description'],
                item_data['image_path']
            ))
        print("✅ เพิ่มข้อมูลตัวอย่าง 10 รายการเรียบร้อย!")


if __name__ == "__main__":
    print("กำลังเริ่มต้นระบบ...")
    init_database()
    create_placeholder_image()
    init_sample_data()
    print("✅ พร้อมใช้งาน! รัน: streamlit run app.py")
