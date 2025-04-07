from abc import ABC, abstractmethod
from .models import Product, Order, Warehouse, StockItem, StockMovement

class ProductRepository(ABC):
    @abstractmethod
    def add(self, product: Product):
        pass

    @abstractmethod
    def get(self, product_id: int) -> Product:
        pass

    @abstractmethod
    def list(self):
        pass

class OrderRepository(ABC):
    @abstractmethod
    def add(self, order: Order):
        pass

    @abstractmethod
    def get(self, order_id: int) -> Order:
        pass

    @abstractmethod
    def list(self):
        pass

class WarehouseRepository(ABC):
    @abstractmethod
    def add(self, warehouse: Warehouse):
        pass

    @abstractmethod
    def get(self, warehouse_id: int) -> Warehouse:
        pass

    @abstractmethod
    def list(self):
        pass

class StockItemRepository(ABC):
    @abstractmethod
    def add(self, stock_item: StockItem):
        pass

    @abstractmethod
    def get(self, stock_item_id: int) -> StockItem:
        pass

    @abstractmethod
    def get_by_product_and_warehouse(self, product_id: int, warehouse_id: int) -> StockItem:
        pass

    @abstractmethod
    def list(self):
        pass

class StockMovementRepository(ABC):
    @abstractmethod
    def add(self, movement: StockMovement):
        pass

    @abstractmethod
    def get(self, movement_id: int) -> StockMovement:
        pass

    @abstractmethod
    def list(self):
        pass

    @abstractmethod
    def list_by_product(self, product_id: int):
        pass

    @abstractmethod
    def list_by_warehouse(self, warehouse_id: int):
        pass
    


