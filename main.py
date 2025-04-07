from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from domain.models import Product, Order, Warehouse, StockItem, StockMovement, MovementType
from domain.services import WarehouseService
from infrastructure.orm import Base, ProductORM, OrderORM
from infrastructure.repositories import SqlAlchemyProductRepository, SqlAlchemyOrderRepository
from infrastructure.unit_of_work import SqlAlchemyUnitOfWork
from infrastructure.database import DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionFactory = sessionmaker(bind=engine)
Base.metadata.create_all(engine)

def main():
    session = SessionFactory()
    product_repo = SqlAlchemyProductRepository(session)
    order_repo = SqlAlchemyOrderRepository(session)

    uow = SqlAlchemyUnitOfWork(session)

    warehouse_service = WarehouseService(
        product_repo=product_repo,
        order_repo=order_repo,
        warehouse_repo=uow.warehouses,
        stock_item_repo=uow.stock_items,
        stock_movement_repo=uow.stock_movements
    )

    with uow:
        # Create products
        laptop = warehouse_service.create_product(name="Laptop", quantity=100, price=1000.0)
        phone = warehouse_service.create_product(name="Phone", quantity=200, price=500.0)
        tablet = warehouse_service.create_product(name="Tablet", quantity=150, price=300.0)
        print("Created products:", laptop.name, phone.name, tablet.name)

        # Create warehouses
        moscow_warehouse = warehouse_service.create_warehouse(
            name="Moscow Warehouse",
            location="Moscow",
            capacity=1000
        )
        spb_warehouse = warehouse_service.create_warehouse(
            name="St. Petersburg Warehouse",
            location="St. Petersburg",
            capacity=800
        )
        print("Created warehouses:", moscow_warehouse.name, spb_warehouse.name)

        # Add stock to warehouses
        moscow_laptop = warehouse_service.add_stock_to_warehouse(
            product=laptop,
            warehouse=moscow_warehouse,
            quantity=50
        )
        moscow_phone = warehouse_service.add_stock_to_warehouse(
            product=phone,
            warehouse=moscow_warehouse,
            quantity=100
        )
        spb_tablet = warehouse_service.add_stock_to_warehouse(
            product=tablet,
            warehouse=spb_warehouse,
            quantity=75
        )
        print(f"Added stock: {moscow_laptop.quantity} laptops to Moscow, "
              f"{moscow_phone.quantity} phones to Moscow, "
              f"{spb_tablet.quantity} tablets to St. Petersburg")

        # Reserve some stock
        reserved_laptops = warehouse_service.reserve_stock(
            product=laptop,
            warehouse=moscow_warehouse,
            quantity=10
        )
        print(f"Reserved {reserved_laptops.reserved_quantity} laptops in Moscow")

        # Transfer stock between warehouses
        transfer = warehouse_service.transfer_stock(
            product=tablet,
            source_warehouse=spb_warehouse,
            destination_warehouse=moscow_warehouse,
            quantity=25
        )
        print(f"Transferred {transfer.quantity} tablets from St. Petersburg to Moscow")

        # Create an order
        order = warehouse_service.create_order(products=[laptop, phone])
        print(f"Created order with {len(order.products)} products")

        # Release reserved stock
        released = warehouse_service.release_reserved_stock(
            product=laptop,
            warehouse=moscow_warehouse,
            quantity=5
        )
        print(f"Released {released.reserved_quantity} laptops from reservation")

        uow.commit()
        print("All operations completed successfully")

if __name__ == "__main__":
    main()


