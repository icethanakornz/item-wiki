from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Item:
    id: Optional[int] = None
    name: str = ""
    type: str = ""
    rarity: str = ""
    drop_location: str = ""
    tier: str = ""
    description: str = ""
    image_path: str = "assets/images/placeholder.png"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @staticmethod
    def from_dict(data: dict):
        return Item(
            id=data.get('id'),
            name=data.get('name', ''),
            type=data.get('type', ''),
            rarity=data.get('rarity', ''),
            drop_location=data.get('drop_location', ''),
            tier=data.get('tier', ''),
            description=data.get('description', ''),
            image_path=data.get('image_path', 'assets/images/placeholder.png'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'rarity': self.rarity,
            'drop_location': self.drop_location,
            'tier': self.tier,
            'description': self.description,
            'image_path': self.image_path
        }
