from sqlalchemy.orm import Session
from domain.unit_of_work import UnitOfWork
from .repositories import (
    SqlAlchemyProductRepository,
    SqlAlchemyOrderRepository,
    SqlAlchemyWarehouseRepository,
    SqlAlchemyStockItemRepository,
    SqlAlchemyStockMovementRepository
)

class SqlAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session: Session):
        self.session = session
        self.products = SqlAlchemyProductRepository(session)
        self.orders = SqlAlchemyOrderRepository(session)
        self.warehouses = SqlAlchemyWarehouseRepository(session)
        self.stock_items = SqlAlchemyStockItemRepository(session)
        self.stock_movements = SqlAlchemyStockMovementRepository(session)
        self._committed = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None or not self._committed:
            self.rollback()
        self.session.close()

    def commit(self):
        self.session.commit()
        self._committed = True

    def rollback(self):
        self.session.rollback()
        self._committed = False