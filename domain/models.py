from dataclasses import dataclass, field
from typing import List, ForwardRef
from datetime import datetime
from enum import Enum

class MovementType(Enum):
    RECEIPT = "receipt"
    SHIPMENT = "shipment"
    TRANSFER = "transfer"

@dataclass
class Product:
    id: int
    name: str
    quantity: int
    price: float

@dataclass
class Order:
    id: int
    products: list[Product] = field(default_factory=list)

    def add_product(self, product: Product):
        self.products.append(product)

@dataclass
class Warehouse:
    id: int
    name: str
    location: str
    capacity: int
    stock_items: list["StockItem"] = field(default_factory=list)

@dataclass
class StockItem:
    id: int
    product: Product
    warehouse: Warehouse
    quantity: int
    reserved_quantity: int = 0

    def reserve(self, quantity: int) -> None:
        if self.quantity - self.reserved_quantity < quantity:
            raise ValueError("Not enough stock available")
        self.reserved_quantity += quantity

    def release_reservation(self, quantity: int) -> None:
        if self.reserved_quantity < quantity:
            raise ValueError("Cannot release more than reserved")
        self.reserved_quantity -= quantity

@dataclass
class StockMovement:
    id: int
    product: Product
    source_warehouse: Warehouse
    destination_warehouse: Warehouse
    quantity: int
    movement_type: MovementType
    timestamp: datetime = field(default_factory=datetime.now)