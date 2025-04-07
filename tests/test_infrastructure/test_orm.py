import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from domain.models import MovementType
from infrastructure.orm import Base, ProductORM, WarehouseORM, StockItemORM, StockMovementORM, OrderORM

@pytest.fixture
def session():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

def test_product_orm_creation(session):
    product = ProductORM(name="Test Product", quantity=10, price=100.0)
    session.add(product)
    session.commit()
    
    retrieved = session.query(ProductORM).first()
    assert retrieved.name == "Test Product"
    assert retrieved.quantity == 10
    assert retrieved.price == 100.0

def test_warehouse_orm_creation(session):
    warehouse = WarehouseORM(name="Main Warehouse", location="Moscow", capacity=1000)
    session.add(warehouse)
    session.commit()
    
    retrieved = session.query(WarehouseORM).first()
    assert retrieved.name == "Main Warehouse"
    assert retrieved.location == "Moscow"
    assert retrieved.capacity == 1000

def test_stock_item_orm_creation(session):
    product = ProductORM(name="Test Product", quantity=10, price=100.0)
    warehouse = WarehouseORM(name="Main Warehouse", location="Moscow", capacity=1000)
    session.add_all([product, warehouse])
    session.commit()
    
    stock_item = StockItemORM(
        product_id=product.id,
        warehouse_id=warehouse.id,
        quantity=5,
        reserved_quantity=2
    )
    session.add(stock_item)
    session.commit()
    
    retrieved = session.query(StockItemORM).first()
    assert retrieved.quantity == 5
    assert retrieved.reserved_quantity == 2
    assert retrieved.product_id == product.id
    assert retrieved.warehouse_id == warehouse.id

def test_stock_movement_orm_creation(session):
    product = ProductORM(name="Test Product", quantity=10, price=100.0)
    source_warehouse = WarehouseORM(name="Source Warehouse", location="Moscow", capacity=1000)
    dest_warehouse = WarehouseORM(name="Dest Warehouse", location="St. Petersburg", capacity=1000)
    session.add_all([product, source_warehouse, dest_warehouse])
    session.commit()
    
    movement = StockMovementORM(
        product_id=product.id,
        source_warehouse_id=source_warehouse.id,
        destination_warehouse_id=dest_warehouse.id,
        quantity=5,
        movement_type=MovementType.TRANSFER,
        timestamp=datetime.now()
    )
    session.add(movement)
    session.commit()
    
    retrieved = session.query(StockMovementORM).first()
    assert retrieved.quantity == 5
    assert retrieved.movement_type == MovementType.TRANSFER
    assert retrieved.product_id == product.id
    assert retrieved.source_warehouse_id == source_warehouse.id
    assert retrieved.destination_warehouse_id == dest_warehouse.id

def test_order_orm_with_products(session):
    product1 = ProductORM(name="Product 1", quantity=10, price=100.0)
    product2 = ProductORM(name="Product 2", quantity=20, price=200.0)
    session.add_all([product1, product2])
    session.commit()
    
    order = OrderORM()
    order.products = [product1, product2]
    session.add(order)
    session.commit()
    
    retrieved = session.query(OrderORM).first()
    assert len(retrieved.products) == 2
    assert {p.name for p in retrieved.products} == {"Product 1", "Product 2"}

def test_warehouse_stock_items_relationship(session):
    warehouse = WarehouseORM(name="Main Warehouse", location="Moscow", capacity=1000)
    product = ProductORM(name="Test Product", quantity=10, price=100.0)
    session.add_all([warehouse, product])
    session.commit()
    
    stock_item = StockItemORM(
        product_id=product.id,
        warehouse_id=warehouse.id,
        quantity=5
    )
    session.add(stock_item)
    session.commit()
    
    retrieved = session.query(WarehouseORM).first()
    assert len(retrieved.stock_items) == 1
    assert retrieved.stock_items[0].quantity == 5
