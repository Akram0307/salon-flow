"""Inventory Management API Router"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.api.dependencies import get_current_user, require_role, get_salon_id
from app.schemas.inventory import (
    ProductCreate, ProductUpdate, ProductResponse,
    StockTransactionCreate, StockTransactionResponse,
    PurchaseOrderCreate, PurchaseOrderUpdate, PurchaseOrderResponse,
    InventoryAlertResponse, InventorySummary,
    ProductCategory, StockStatus, StockTransactionType, PurchaseOrderStatus
)
from app.models.inventory import Product, StockTransaction, PurchaseOrder, InventoryAlert
import uuid
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/inventory", tags=["Inventory"])


# ==================== Products ====================

@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    data: ProductCreate,
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(require_role(["owner", "manager"]))
):
    """Create a new product in inventory"""
    product_id = str(uuid.uuid4())
    
    # Check if SKU already exists for this salon
    existing = await Product.find_by_field("sku", data.sku, salon_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Product with SKU '{data.sku}' already exists"
        )
    
    product_data = data.model_dump()
    product_data["product_id"] = product_id
    product_data["salon_id"] = salon_id
    product_data["current_quantity"] = data.initial_quantity
    product_data.pop("initial_quantity", None)
    
    product = Product(**product_data)
    product.update_stock_status()
    
    if data.initial_quantity > 0:
        product.last_restocked_at = datetime.utcnow()
    
    await product.save()
    
    # Create alert if low stock
    if product.stock_status == StockStatus.LOW_STOCK.value:
        await _create_low_stock_alert(product)
    
    return ProductResponse(**product.to_dict())


@router.get("/products", response_model=List[ProductResponse])
async def list_products(
    category: Optional[ProductCategory] = Query(None),
    status: Optional[StockStatus] = Query(None),
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0),
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(get_current_user)
):
    """List all products with optional filters"""
    filters = {"salon_id": salon_id}
    
    if category:
        filters["category"] = category.value
    if status:
        filters["stock_status"] = status.value
    if is_active is not None:
        filters["is_active"] = is_active
    
    products = await Product.find_all(**filters, limit=limit, offset=offset)
    
    if search:
        search_lower = search.lower()
        products = [
            p for p in products
            if search_lower in p.name.lower() or search_lower in p.sku.lower()
        ]
    
    return [ProductResponse(**p.to_dict()) for p in products]


@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: str,
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(get_current_user)
):
    """Get a specific product by ID"""
    product = await Product.find_by_id(product_id, salon_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return ProductResponse(**product.to_dict())


@router.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: str,
    data: ProductUpdate,
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(require_role(["owner", "manager"]))
):
    """Update a product"""
    product = await Product.find_by_id(product_id, salon_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
    
    product.updated_at = datetime.utcnow()
    await product.save()
    
    return ProductResponse(**product.to_dict())


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: str,
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(require_role(["owner", "manager"]))
):
    """Delete a product (soft delete by setting is_active=False)"""
    product = await Product.find_by_id(product_id, salon_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    product.is_active = False
    product.updated_at = datetime.utcnow()
    await product.save()


# ==================== Stock Transactions ====================

@router.post("/transactions", response_model=StockTransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_stock_transaction(
    data: StockTransactionCreate,
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(require_role(["owner", "manager", "receptionist"]))
):
    """Create a stock transaction (purchase, usage, adjustment, etc.)"""
    # Verify product exists
    product = await Product.find_by_id(data.product_id, salon_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    transaction_id = str(uuid.uuid4())
    previous_quantity = product.current_quantity
    
    # Calculate new quantity
    if data.transaction_type in [StockTransactionType.PURCHASE, StockTransactionType.RETURN]:
        new_quantity = previous_quantity + abs(data.quantity)
    elif data.transaction_type in [StockTransactionType.SALE, StockTransactionType.USAGE, 
                                    StockTransactionType.DAMAGE, StockTransactionType.TRANSFER]:
        new_quantity = previous_quantity - abs(data.quantity)
        if new_quantity < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock. Current: {previous_quantity}, Requested: {abs(data.quantity)}"
            )
    else:  # ADJUSTMENT
        new_quantity = previous_quantity + data.quantity
    
    # Update product stock
    product.current_quantity = new_quantity
    old_status = product.stock_status
    product.update_stock_status()
    
    if data.transaction_type == StockTransactionType.PURCHASE:
        product.last_restocked_at = datetime.utcnow()
    
    product.updated_at = datetime.utcnow()
    await product.save()
    
    # Create transaction record
    transaction_data = data.model_dump()
    transaction_data["transaction_id"] = transaction_id
    transaction_data["salon_id"] = salon_id
    transaction_data["previous_quantity"] = previous_quantity
    transaction_data["new_quantity"] = new_quantity
    transaction_data["created_by"] = user.get("uid")
    
    unit_price = data.unit_price or product.cost_price
    transaction_data["total_value"] = abs(data.quantity) * unit_price
    
    transaction = StockTransaction(**transaction_data)
    await transaction.save()
    
    # Create alerts for low stock
    if old_status != StockStatus.LOW_STOCK.value and product.stock_status == StockStatus.LOW_STOCK.value:
        await _create_low_stock_alert(product)
    elif old_status != StockStatus.OUT_OF_STOCK.value and product.stock_status == StockStatus.OUT_OF_STOCK.value:
        await _create_out_of_stock_alert(product)
    
    return StockTransactionResponse(**transaction.to_dict())


@router.get("/transactions", response_model=List[StockTransactionResponse])
async def list_transactions(
    product_id: Optional[str] = Query(None),
    transaction_type: Optional[StockTransactionType] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0),
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(get_current_user)
):
    """List stock transactions with filters"""
    filters = {"salon_id": salon_id}
    
    if product_id:
        filters["product_id"] = product_id
    if transaction_type:
        filters["transaction_type"] = transaction_type.value
    
    transactions = await StockTransaction.find_all(**filters, limit=limit, offset=offset)
    
    # Filter by date range
    if start_date or end_date:
        filtered = []
        for t in transactions:
            if start_date and t.created_at < start_date:
                continue
            if end_date and t.created_at > end_date:
                continue
            filtered.append(t)
        transactions = filtered
    
    return [StockTransactionResponse(**t.to_dict()) for t in transactions]


# ==================== Purchase Orders ====================

@router.post("/purchase-orders", response_model=PurchaseOrderResponse, status_code=status.HTTP_201_CREATED)
async def create_purchase_order(
    data: PurchaseOrderCreate,
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(require_role(["owner", "manager"]))
):
    """Create a new purchase order"""
    order_id = str(uuid.uuid4())
    order_number = f"PO-{datetime.utcnow().strftime('%Y%m%d')}-{order_id[:8].upper()}"
    
    # Process items
    items = []
    for item_data in data.items:
        product = await Product.find_by_id(item_data.product_id, salon_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product {item_data.product_id} not found"
            )
        
        item_dict = {
            "id": str(uuid.uuid4()),
            "product_id": item_data.product_id,
            "product_name": product.name,
            "product_sku": product.sku,
            "quantity": item_data.quantity,
            "unit_price": item_data.unit_price,
            "gst_rate": item_data.gst_rate
        }
        items.append(item_dict)
    
    order_data = data.model_dump()
    order_data["order_id"] = order_id
    order_data["order_number"] = order_number
    order_data["salon_id"] = salon_id
    order_data["items"] = items
    order_data["created_by"] = user.get("uid")
    
    order = PurchaseOrder(**order_data)
    order.calculate_totals()
    await order.save()
    
    return PurchaseOrderResponse(**order.to_dict())


@router.get("/purchase-orders", response_model=List[PurchaseOrderResponse])
async def list_purchase_orders(
    status: Optional[PurchaseOrderStatus] = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0),
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(get_current_user)
):
    """List purchase orders"""
    filters = {"salon_id": salon_id}
    
    if status:
        filters["status"] = status.value
    
    orders = await PurchaseOrder.find_all(**filters, limit=limit, offset=offset)
    return [PurchaseOrderResponse(**o.to_dict()) for o in orders]


@router.get("/purchase-orders/{order_id}", response_model=PurchaseOrderResponse)
async def get_purchase_order(
    order_id: str,
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(get_current_user)
):
    """Get a specific purchase order"""
    order = await PurchaseOrder.find_by_id(order_id, salon_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase order not found"
        )
    return PurchaseOrderResponse(**order.to_dict())


@router.put("/purchase-orders/{order_id}", response_model=PurchaseOrderResponse)
async def update_purchase_order(
    order_id: str,
    data: PurchaseOrderUpdate,
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(require_role(["owner", "manager"]))
):
    """Update a purchase order"""
    order = await PurchaseOrder.find_by_id(order_id, salon_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase order not found"
        )
    
    if order.status not in [PurchaseOrderStatus.DRAFT.value, PurchaseOrderStatus.PENDING.value]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update order that is already approved or processed"
        )
    
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(order, field, value)
    
    order.updated_at = datetime.utcnow()
    await order.save()
    
    return PurchaseOrderResponse(**order.to_dict())


@router.post("/purchase-orders/{order_id}/receive", response_model=PurchaseOrderResponse)
async def receive_purchase_order(
    order_id: str,
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(require_role(["owner", "manager"]))
):
    """Mark purchase order as received and update inventory"""
    order = await PurchaseOrder.find_by_id(order_id, salon_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase order not found"
        )
    
    if order.status != PurchaseOrderStatus.ORDERED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order must be in 'ordered' status to receive"
        )
    
    # Process each item
    for item_data in order.items:
        product = await Product.find_by_id(item_data["product_id"], salon_id)
        if product:
            # Create stock transaction
            transaction = StockTransaction(
                transaction_id=str(uuid.uuid4()),
                product_id=product.product_id,
                salon_id=salon_id,
                transaction_type=StockTransactionType.PURCHASE.value,
                quantity=item_data["quantity"],
                previous_quantity=product.current_quantity,
                new_quantity=product.current_quantity + item_data["quantity"],
                unit_price=Decimal(str(item_data["unit_price"])),
                total_value=Decimal(str(item_data["quantity"])) * Decimal(str(item_data["unit_price"])),
                reference_type="purchase_order",
                reference_id=order_id,
                created_by=user.get("uid")
            )
            await transaction.save()
            
            # Update product stock
            product.current_quantity += item_data["quantity"]
            product.last_restocked_at = datetime.utcnow()
            product.update_stock_status()
            product.updated_at = datetime.utcnow()
            await product.save()
    
    # Update order status
    order.status = PurchaseOrderStatus.RECEIVED.value
    order.updated_at = datetime.utcnow()
    await order.save()
    
    return PurchaseOrderResponse(**order.to_dict())


# ==================== Alerts ====================

@router.get("/alerts", response_model=List[InventoryAlertResponse])
async def list_alerts(
    is_resolved: Optional[bool] = Query(None),
    limit: int = Query(50, le=100),
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(get_current_user)
):
    """List inventory alerts"""
    filters = {"salon_id": salon_id}
    
    if is_resolved is not None:
        filters["is_resolved"] = is_resolved
    
    alerts = await InventoryAlert.find_all(**filters, limit=limit)
    return [InventoryAlertResponse(**a.to_dict()) for a in alerts]


@router.post("/alerts/{alert_id}/resolve", response_model=InventoryAlertResponse)
async def resolve_alert(
    alert_id: str,
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(require_role(["owner", "manager"]))
):
    """Mark an alert as resolved"""
    alert = await InventoryAlert.find_by_id(alert_id, salon_id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    alert.is_resolved = True
    alert.resolved_by = user.get("uid")
    alert.resolved_at = datetime.utcnow()
    await alert.save()
    
    return InventoryAlertResponse(**alert.to_dict())


# ==================== Summary ====================

@router.get("/summary", response_model=InventorySummary)
async def get_inventory_summary(
    salon_id: str = Depends(get_salon_id),
    user: dict = Depends(get_current_user)
):
    """Get inventory summary statistics"""
    products = await Product.find_all(salon_id=salon_id, is_active=True)
    
    total_products = len(products)
    total_value = sum(p.current_quantity * p.cost_price for p in products)
    low_stock_count = sum(1 for p in products if p.stock_status == StockStatus.LOW_STOCK.value)
    out_of_stock_count = sum(1 for p in products if p.stock_status == StockStatus.OUT_OF_STOCK.value)
    
    # Category breakdown
    category_breakdown = {}
    for p in products:
        cat = p.category
        if cat not in category_breakdown:
            category_breakdown[cat] = {"count": 0, "value": 0}
        category_breakdown[cat]["count"] += 1
        category_breakdown[cat]["value"] += float(p.current_quantity * p.cost_price)
    
    # Pending orders
    pending_orders = await PurchaseOrder.find_all(
        salon_id=salon_id,
        status=PurchaseOrderStatus.PENDING.value
    )
    
    return InventorySummary(
        total_products=total_products,
        total_value=total_value,
        low_stock_count=low_stock_count,
        out_of_stock_count=out_of_stock_count,
        pending_orders=len(pending_orders),
        category_breakdown=category_breakdown
    )


# ==================== Helper Functions ====================

async def _create_low_stock_alert(product: Product):
    """Create a low stock alert"""
    alert = InventoryAlert(
        alert_id=str(uuid.uuid4()),
        product_id=product.product_id,
        salon_id=product.salon_id,
        alert_type="low_stock",
        message=f"Product '{product.name}' (SKU: {product.sku}) is running low. Current stock: {product.current_quantity}, Reorder point: {product.reorder_point}"
    )
    await alert.save()


async def _create_out_of_stock_alert(product: Product):
    """Create an out of stock alert"""
    alert = InventoryAlert(
        alert_id=str(uuid.uuid4()),
        product_id=product.product_id,
        salon_id=product.salon_id,
        alert_type="out_of_stock",
        message=f"Product '{product.name}' (SKU: {product.sku}) is out of stock!"
    )
    await alert.save()
