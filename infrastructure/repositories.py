from sqlalchemy.orm import Session
from typing import List
from domain.models import Order, Product, Warehouse, StockItem, StockMovement
from domain.repositories import (
    ProductRepository, OrderRepository, WarehouseRepository,
    StockItemRepository, StockMovementRepository
)
from .orm import ProductORM, OrderORM, WarehouseORM, StockItemORM, StockMovementORM

class SqlAlchemyProductRepository(ProductRepository):
    def __init__(self, session: Session):
        self.session = session

    def add(self, product: Product):
        product_orm = ProductORM(
            name=product.name,
            quantity=product.quantity,
            price=product.price
        )
        self.session.add(product_orm)

    def get(self, product_id: int) -> Product:
        product_orm = self.session.query(ProductORM).filter_by(id=product_id).one()
        return Product(
            id=product_orm.id,
            name=product_orm.name,
            quantity=product_orm.quantity,
            price=product_orm.price
        )

    def list(self) -> List[Product]:
        products_orm = self.session.query(ProductORM).all()
        return [
            Product(id=p.id, name=p.name, quantity=p.quantity, price=p.price)
            for p in products_orm
        ]

class SqlAlchemyOrderRepository(OrderRepository):
    def __init__(self, session: Session):
        self.session = session

    def add(self, order: Order):
        order_orm = OrderORM()
        order_orm.products = [
            self.session.query(ProductORM).filter_by(id=p.id).one()
            for p in order.products
        ]
        self.session.add(order_orm)

    def get(self, order_id: int) -> Order:
        order_orm = self.session.query(OrderORM).filter_by(id=order_id).one()
        products = [
            Product(id=p.id, name=p.name, quantity=p.quantity, price=p.price)
            for p in order_orm.products
        ]
        return Order(id=order_orm.id, products=products)

    def list(self) -> List[Order]:
        orders_orm = self.session.query(OrderORM).all()
        orders = []
        for order_orm in orders_orm:
            products = [
                Product(id=p.id, name=p.name, quantity=p.quantity, price=p.price)
                for p in order_orm.products
            ]
            orders.append(Order(id=order_orm.id, products=products))
        return orders

class SqlAlchemyWarehouseRepository(WarehouseRepository):
    def __init__(self, session: Session):
        self.session = session

    def add(self, warehouse: Warehouse):
        warehouse_orm = WarehouseORM(
            name=warehouse.name,
            location=warehouse.location,
            capacity=warehouse.capacity
        )
        self.session.add(warehouse_orm)

    def get(self, warehouse_id: int) -> Warehouse:
        warehouse_orm = self.session.query(WarehouseORM).filter_by(id=warehouse_id).one()
        return Warehouse(
            id=warehouse_orm.id,
            name=warehouse_orm.name,
            location=warehouse_orm.location,
            capacity=warehouse_orm.capacity
        )

    def list(self) -> List[Warehouse]:
        warehouses_orm = self.session.query(WarehouseORM).all()
        return [
            Warehouse(
                id=w.id,
                name=w.name,
                location=w.location,
                capacity=w.capacity
            )
            for w in warehouses_orm
        ]

class SqlAlchemyStockItemRepository(StockItemRepository):
    def __init__(self, session: Session):
        self.session = session

    def add(self, stock_item: StockItem):
        stock_item_orm = StockItemORM(
            product_id=stock_item.product.id,
            warehouse_id=stock_item.warehouse.id,
            quantity=stock_item.quantity,
            reserved_quantity=stock_item.reserved_quantity
        )
        self.session.add(stock_item_orm)

    def get(self, stock_item_id: int) -> StockItem:
        stock_item_orm = self.session.query(StockItemORM).filter_by(id=stock_item_id).one()
        return self._to_domain(stock_item_orm)

    def get_by_product_and_warehouse(self, product_id: int, warehouse_id: int) -> StockItem:
        stock_item_orm = self.session.query(StockItemORM).filter_by(
            product_id=product_id,
            warehouse_id=warehouse_id
        ).one()
        return self._to_domain(stock_item_orm)

    def list(self) -> List[StockItem]:
        stock_items_orm = self.session.query(StockItemORM).all()
        return [self._to_domain(si) for si in stock_items_orm]

    def _to_domain(self, stock_item_orm: StockItemORM) -> StockItem:
        product = Product(
            id=stock_item_orm.product.id,
            name=stock_item_orm.product.name,
            quantity=stock_item_orm.product.quantity,
            price=stock_item_orm.product.price
        )
        warehouse = Warehouse(
            id=stock_item_orm.warehouse.id,
            name=stock_item_orm.warehouse.name,
            location=stock_item_orm.warehouse.location,
            capacity=stock_item_orm.warehouse.capacity
        )
        return StockItem(
            id=stock_item_orm.id,
            product=product,
            warehouse=warehouse,
            quantity=stock_item_orm.quantity,
            reserved_quantity=stock_item_orm.reserved_quantity
        )

class SqlAlchemyStockMovementRepository(StockMovementRepository):
    def __init__(self, session: Session):
        self.session = session

    def add(self, movement: StockMovement):
        movement_orm = StockMovementORM(
            product_id=movement.product.id,
            source_warehouse_id=movement.source_warehouse.id,
            destination_warehouse_id=movement.destination_warehouse.id,
            quantity=movement.quantity,
            movement_type=movement.movement_type,
            timestamp=movement.timestamp
        )
        self.session.add(movement_orm)

    def get(self, movement_id: int) -> StockMovement:
        movement_orm = self.session.query(StockMovementORM).filter_by(id=movement_id).one()
        return self._to_domain(movement_orm)

    def list(self) -> List[StockMovement]:
        movements_orm = self.session.query(StockMovementORM).all()
        return [self._to_domain(m) for m in movements_orm]

    def list_by_product(self, product_id: int) -> List[StockMovement]:
        movements_orm = self.session.query(StockMovementORM).filter_by(product_id=product_id).all()
        return [self._to_domain(m) for m in movements_orm]

    def list_by_warehouse(self, warehouse_id: int) -> List[StockMovement]:
        movements_orm = self.session.query(StockMovementORM).filter(
            (StockMovementORM.source_warehouse_id == warehouse_id) |
            (StockMovementORM.destination_warehouse_id == warehouse_id)
        ).all()
        return [self._to_domain(m) for m in movements_orm]

    def _to_domain(self, movement_orm: StockMovementORM) -> StockMovement:
        product = Product(
            id=movement_orm.product.id,
            name=movement_orm.product.name,
            quantity=movement_orm.product.quantity,
            price=movement_orm.product.price
        )
        source_warehouse = Warehouse(
            id=movement_orm.source_warehouse.id,
            name=movement_orm.source_warehouse.name,
            location=movement_orm.source_warehouse.location,
            capacity=movement_orm.source_warehouse.capacity
        )
        destination_warehouse = Warehouse(
            id=movement_orm.destination_warehouse.id,
            name=movement_orm.destination_warehouse.name,
            location=movement_orm.destination_warehouse.location,
            capacity=movement_orm.destination_warehouse.capacity
        )
        return StockMovement(
            id=movement_orm.id,
            product=product,
            source_warehouse=source_warehouse,
            destination_warehouse=destination_warehouse,
            quantity=movement_orm.quantity,
            movement_type=movement_orm.movement_type,
            timestamp=movement_orm.timestamp
        )





