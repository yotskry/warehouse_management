import pytest
from datetime import datetime
from domain.models import Product, Order, Warehouse, StockItem, StockMovement, MovementType
from domain.services import WarehouseService
from domain.repositories import (
    ProductRepository, OrderRepository, WarehouseRepository,
    StockItemRepository, StockMovementRepository
)

class MockProductRepository(ProductRepository):
    def __init__(self):
        self.products = []
        self.next_id = 1

    def add(self, product: Product):
        product.id = self.next_id
        self.products.append(product)
        self.next_id += 1

    def get(self, product_id: int) -> Product:
        return next(p for p in self.products if p.id == product_id)

    def list(self):
        return self.products

class MockOrderRepository(OrderRepository):
    def __init__(self):
        self.orders = []
        self.next_id = 1

    def add(self, order: Order):
        order.id = self.next_id
        self.orders.append(order)
        self.next_id += 1

    def get(self, order_id: int) -> Order:
        return next(o for o in self.orders if o.id == order_id)

    def list(self):
        return self.orders

class MockWarehouseRepository(WarehouseRepository):
    def __init__(self):
        self.warehouses = []
        self.next_id = 1

    def add(self, warehouse: Warehouse):
        warehouse.id = self.next_id
        self.warehouses.append(warehouse)
        self.next_id += 1

    def get(self, warehouse_id: int) -> Warehouse:
        return next(w for w in self.warehouses if w.id == warehouse_id)

    def list(self):
        return self.warehouses

class MockStockItemRepository(StockItemRepository):
    def __init__(self):
        self.stock_items = []
        self.next_id = 1

    def add(self, stock_item: StockItem):
        stock_item.id = self.next_id
        self.stock_items.append(stock_item)
        self.next_id += 1

    def get(self, stock_item_id: int) -> StockItem:
        return next(si for si in self.stock_items if si.id == stock_item_id)

    def get_by_product_and_warehouse(self, product_id: int, warehouse_id: int) -> StockItem:
        return next(
            si for si in self.stock_items
            if si.product.id == product_id and si.warehouse.id == warehouse_id
        )

    def list(self):
        return self.stock_items

class MockStockMovementRepository(StockMovementRepository):
    def __init__(self):
        self.movements = []
        self.next_id = 1

    def add(self, movement: StockMovement):
        movement.id = self.next_id
        self.movements.append(movement)
        self.next_id += 1

    def get(self, movement_id: int) -> StockMovement:
        return next(m for m in self.movements if m.id == movement_id)

    def list(self):
        return self.movements

    def list_by_product(self, product_id: int):
        return [m for m in self.movements if m.product.id == product_id]

    def list_by_warehouse(self, warehouse_id: int):
        return [
            m for m in self.movements
            if m.source_warehouse.id == warehouse_id or m.destination_warehouse.id == warehouse_id
        ]

@pytest.fixture
def repositories():
    return {
        'products': MockProductRepository(),
        'orders': MockOrderRepository(),
        'warehouses': MockWarehouseRepository(),
        'stock_items': MockStockItemRepository(),
        'stock_movements': MockStockMovementRepository()
    }

@pytest.fixture
def service(repositories):
    return WarehouseService(
        product_repo=repositories['products'],
        order_repo=repositories['orders'],
        warehouse_repo=repositories['warehouses'],
        stock_item_repo=repositories['stock_items'],
        stock_movement_repo=repositories['stock_movements']
    )

def test_create_product(service, repositories):
    product = service.create_product(name="Test Product", quantity=10, price=100.0)
    
    assert product.name == "Test Product"
    assert product.quantity == 10
    assert product.price == 100.0
    assert len(repositories['products'].list()) == 1

def test_create_order(service, repositories):
    product1 = service.create_product(name="Product 1", quantity=10, price=100.0)
    product2 = service.create_product(name="Product 2", quantity=20, price=200.0)
    
    order = service.create_order(products=[product1, product2])
    
    assert len(order.products) == 2
    assert {p.name for p in order.products} == {"Product 1", "Product 2"}
    assert len(repositories['orders'].list()) == 1

def test_create_warehouse(service, repositories):
    warehouse = service.create_warehouse(name="Main Warehouse", location="Moscow", capacity=1000)
    
    assert warehouse.name == "Main Warehouse"
    assert warehouse.location == "Moscow"
    assert warehouse.capacity == 1000
    assert len(repositories['warehouses'].list()) == 1

def test_add_stock_to_warehouse(service, repositories):
    product = service.create_product(name="Test Product", quantity=10, price=100.0)
    warehouse = service.create_warehouse(name="Main Warehouse", location="Moscow", capacity=1000)
    
    stock_item = service.add_stock_to_warehouse(
        product=product,
        warehouse=warehouse,
        quantity=5
    )
    
    assert stock_item.quantity == 5
    assert stock_item.product.id == product.id
    assert stock_item.warehouse.id == warehouse.id
    assert len(repositories['stock_items'].list()) == 1

def test_transfer_stock(service, repositories):
    product = service.create_product(name="Test Product", quantity=10, price=100.0)
    source_warehouse = service.create_warehouse(name="Source", location="Moscow", capacity=1000)
    dest_warehouse = service.create_warehouse(name="Dest", location="SPb", capacity=1000)
    
    service.add_stock_to_warehouse(product, source_warehouse, 10)
    
    movement = service.transfer_stock(
        product=product,
        source_warehouse=source_warehouse,
        destination_warehouse=dest_warehouse,
        quantity=5
    )
    
    assert movement.quantity == 5
    assert movement.movement_type == MovementType.TRANSFER
    assert movement.source_warehouse.id == source_warehouse.id
    assert movement.destination_warehouse.id == dest_warehouse.id
    
    source_stock = repositories['stock_items'].get_by_product_and_warehouse(
        product.id, source_warehouse.id
    )
    dest_stock = repositories['stock_items'].get_by_product_and_warehouse(
        product.id, dest_warehouse.id
    )
    
    assert source_stock.quantity == 5
    assert dest_stock.quantity == 5

def test_reserve_stock(service, repositories):
    product = service.create_product(name="Test Product", quantity=10, price=100.0)
    warehouse = service.create_warehouse(name="Main Warehouse", location="Moscow", capacity=1000)
    
    service.add_stock_to_warehouse(product, warehouse, 10)
    
    stock_item = service.reserve_stock(product, warehouse, 5)
    
    assert stock_item.quantity == 10
    assert stock_item.reserved_quantity == 5

def test_release_reserved_stock(service, repositories):
    product = service.create_product(name="Test Product", quantity=10, price=100.0)
    warehouse = service.create_warehouse(name="Main Warehouse", location="Moscow", capacity=1000)
    
    service.add_stock_to_warehouse(product, warehouse, 10)
    service.reserve_stock(product, warehouse, 5)
    
    stock_item = service.release_reserved_stock(product, warehouse, 3)
    
    assert stock_item.quantity == 10
    assert stock_item.reserved_quantity == 2
