from sqlalchemy import create_engine, Column, Integer, String, Float, Table, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from domain.models import MovementType

Base = declarative_base()

class ProductORM(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    quantity = Column(Integer)
    price = Column(Float)

class WarehouseORM(Base):
    __tablename__ = 'warehouses'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    location = Column(String)
    capacity = Column(Integer)
    stock_items = relationship("StockItemORM", back_populates="warehouse")

class StockItemORM(Base):
    __tablename__ = 'stock_items'
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    warehouse_id = Column(Integer, ForeignKey('warehouses.id'))
    quantity = Column(Integer)
    reserved_quantity = Column(Integer, default=0)
    
    product = relationship("ProductORM")
    warehouse = relationship("WarehouseORM", back_populates="stock_items")

class StockMovementORM(Base):
    __tablename__ = 'stock_movements'
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    source_warehouse_id = Column(Integer, ForeignKey('warehouses.id'))
    destination_warehouse_id = Column(Integer, ForeignKey('warehouses.id'))
    quantity = Column(Integer)
    movement_type = Column(SQLEnum(MovementType))
    timestamp = Column(DateTime)
    
    product = relationship("ProductORM")
    source_warehouse = relationship("WarehouseORM", foreign_keys=[source_warehouse_id])
    destination_warehouse = relationship("WarehouseORM", foreign_keys=[destination_warehouse_id])

class OrderORM(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)

order_product_associations = Table(
    'order_product_associations', Base.metadata,
    Column('order_id', ForeignKey('orders.id')),
    Column('product_id', ForeignKey('products.id'))
)

OrderORM.products = relationship("ProductORM", secondary=order_product_associations)