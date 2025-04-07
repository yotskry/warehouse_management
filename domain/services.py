from .models import Product, Order, Warehouse, StockItem, StockMovement, MovementType
from .repositories import (
    ProductRepository, OrderRepository, WarehouseRepository,
    StockItemRepository, StockMovementRepository
)
from typing import List
from datetime import datetime

class WarehouseService:
    def __init__(
        self,
        product_repo: ProductRepository,
        order_repo: OrderRepository,
        warehouse_repo: WarehouseRepository,
        stock_item_repo: StockItemRepository,
        stock_movement_repo: StockMovementRepository
    ):
        self.product_repo = product_repo
        self.order_repo = order_repo
        self.warehouse_repo = warehouse_repo
        self.stock_item_repo = stock_item_repo
        self.stock_movement_repo = stock_movement_repo

    def create_product(self, name: str, quantity: int, price: float) -> Product:
        product = Product(id=None, name=name, quantity=quantity, price=price)
        self.product_repo.add(product)
        return product

    def create_order(self, products: List[Product]) -> Order:
        order = Order(id=None, products=products)
        self.order_repo.add(order)
        return order

    def create_warehouse(self, name: str, location: str, capacity: int) -> Warehouse:
        warehouse = Warehouse(id=None, name=name, location=location, capacity=capacity)
        self.warehouse_repo.add(warehouse)
        return warehouse

    def add_stock_to_warehouse(self, product: Product, warehouse: Warehouse, quantity: int) -> StockItem:
        try:
            stock_item = self.stock_item_repo.get_by_product_and_warehouse(product.id, warehouse.id)
            stock_item.quantity += quantity
        except StopIteration:
            stock_item = StockItem(
                id=None,
                product=product,
                warehouse=warehouse,
                quantity=quantity,
                reserved_quantity=0
            )
            self.stock_item_repo.add(stock_item)
        return stock_item

    def transfer_stock(
        self,
        product: Product,
        source_warehouse: Warehouse,
        destination_warehouse: Warehouse,
        quantity: int
    ) -> StockMovement:
        source_stock = self.stock_item_repo.get_by_product_and_warehouse(product.id, source_warehouse.id)
        if source_stock.quantity - source_stock.reserved_quantity < quantity:
            raise ValueError("Not enough available stock in source warehouse")

        # Update source warehouse stock
        source_stock.quantity -= quantity

        # Add or update destination warehouse stock
        try:
            dest_stock = self.stock_item_repo.get_by_product_and_warehouse(product.id, destination_warehouse.id)
            dest_stock.quantity += quantity
        except StopIteration:
            dest_stock = StockItem(
                id=None,
                product=product,
                warehouse=destination_warehouse,
                quantity=quantity,
                reserved_quantity=0
            )
            self.stock_item_repo.add(dest_stock)

        # Record the movement
        movement = StockMovement(
            id=None,
            product=product,
            source_warehouse=source_warehouse,
            destination_warehouse=destination_warehouse,
            quantity=quantity,
            movement_type=MovementType.TRANSFER,
            timestamp=datetime.now()
        )
        self.stock_movement_repo.add(movement)
        return movement

    def reserve_stock(self, product: Product, warehouse: Warehouse, quantity: int) -> StockItem:
        stock_item = self.stock_item_repo.get_by_product_and_warehouse(product.id, warehouse.id)
        stock_item.reserve(quantity)
        return stock_item

    def release_reserved_stock(self, product: Product, warehouse: Warehouse, quantity: int) -> StockItem:
        stock_item = self.stock_item_repo.get_by_product_and_warehouse(product.id, warehouse.id)
        stock_item.release_reservation(quantity)
        return stock_item
