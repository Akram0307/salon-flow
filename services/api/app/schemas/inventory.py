"""Inventory Management Schemas"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class ProductCategory(str, Enum):
    HAIR_CARE = "hair_care"
    SKIN_CARE = "skin_care"
    NAIL_CARE = "nail_care"
    MAKEUP = "makeup"
    TOOLS = "tools"
    CONSUMABLES = "consumables"
    OTHER = "other"


class StockStatus(str, Enum):
    IN_STOCK = "in_stock"
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"
    DISCONTINUED = "discontinued"


class ProductBase(BaseModel):
    """Base product schema"""
    name: str = Field(..., min_length=1, max_length=200)
    sku: str = Field(..., min_length=1, max_length=50)
    category: ProductCategory
    description: Optional[str] = None
    unit: str = Field(default="piece", max_length=20)  # piece, ml, gm, etc.
    unit_price: Decimal = Field(..., ge=0)
    cost_price: Decimal = Field(..., ge=0)
    gst_rate: Decimal = Field(default=Decimal("18.00"), ge=0, le=100)
    hsn_code: Optional[str] = Field(None, max_length=10)
    min_stock_level: int = Field(default=5, ge=0)
    max_stock_level: int = Field(default=100, ge=0)
    reorder_point: int = Field(default=10, ge=0)
    is_active: bool = True


class ProductCreate(ProductBase):
    """Schema for creating a product"""
    salon_id: Optional[str] = None  # Injected from auth
    initial_quantity: int = Field(default=0, ge=0)


class ProductUpdate(BaseModel):
    """Schema for updating a product"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    sku: Optional[str] = Field(None, min_length=1, max_length=50)
    category: Optional[ProductCategory] = None
    description: Optional[str] = None
    unit: Optional[str] = Field(None, max_length=20)
    unit_price: Optional[Decimal] = Field(None, ge=0)
    cost_price: Optional[Decimal] = Field(None, ge=0)
    gst_rate: Optional[Decimal] = Field(None, ge=0, le=100)
    hsn_code: Optional[str] = Field(None, max_length=10)
    min_stock_level: Optional[int] = Field(None, ge=0)
    max_stock_level: Optional[int] = Field(None, ge=0)
    reorder_point: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class ProductResponse(ProductBase):
    """Schema for product response"""
    id: str
    salon_id: str
    current_quantity: int = 0
    stock_status: StockStatus = StockStatus.IN_STOCK
    last_restocked_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StockTransactionType(str, Enum):
    PURCHASE = "purchase"
    SALE = "sale"
    USAGE = "usage"  # Used in services
    ADJUSTMENT = "adjustment"  # Manual correction
    RETURN = "return"
    DAMAGE = "damage"
    TRANSFER = "transfer"


class StockTransactionBase(BaseModel):
    """Base stock transaction schema"""
    product_id: str
    transaction_type: StockTransactionType
    quantity: int = Field(..., description="Positive for in, negative for out")
    unit_price: Optional[Decimal] = None
    reference_type: Optional[str] = None  # booking, purchase_order, etc.
    reference_id: Optional[str] = None
    notes: Optional[str] = None


class StockTransactionCreate(StockTransactionBase):
    """Schema for creating a stock transaction"""
    salon_id: Optional[str] = None  # Injected from auth


class StockTransactionResponse(StockTransactionBase):
    """Schema for stock transaction response"""
    id: str
    salon_id: str
    previous_quantity: int
    new_quantity: int
    total_value: Decimal
    created_by: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PurchaseOrderStatus(str, Enum):
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    ORDERED = "ordered"
    RECEIVED = "received"
    CANCELLED = "cancelled"


class PurchaseOrderItemBase(BaseModel):
    """Base purchase order item schema"""
    product_id: str
    quantity: int = Field(..., gt=0)
    unit_price: Decimal = Field(..., ge=0)
    gst_rate: Decimal = Field(default=Decimal("18.00"))


class PurchaseOrderItemCreate(PurchaseOrderItemBase):
    """Schema for creating purchase order item"""
    pass


class PurchaseOrderItemResponse(PurchaseOrderItemBase):
    """Schema for purchase order item response"""
    id: str
    product_name: str
    product_sku: str
    subtotal: Decimal
    gst_amount: Decimal
    total: Decimal

    class Config:
        from_attributes = True


class PurchaseOrderBase(BaseModel):
    """Base purchase order schema"""
    supplier_name: str = Field(..., max_length=200)
    supplier_gstin: Optional[str] = Field(None, max_length=15)
    supplier_address: Optional[str] = None
    supplier_phone: Optional[str] = None
    expected_delivery_date: Optional[datetime] = None
    notes: Optional[str] = None


class PurchaseOrderCreate(PurchaseOrderBase):
    """Schema for creating a purchase order"""
    salon_id: Optional[str] = None  # Injected from auth
    items: List[PurchaseOrderItemCreate]


class PurchaseOrderUpdate(BaseModel):
    """Schema for updating a purchase order"""
    supplier_name: Optional[str] = Field(None, max_length=200)
    supplier_gstin: Optional[str] = Field(None, max_length=15)
    supplier_address: Optional[str] = None
    supplier_phone: Optional[str] = None
    expected_delivery_date: Optional[datetime] = None
    status: Optional[PurchaseOrderStatus] = None
    notes: Optional[str] = None


class PurchaseOrderResponse(PurchaseOrderBase):
    """Schema for purchase order response"""
    id: str
    salon_id: str
    order_number: str
    status: PurchaseOrderStatus
    items: List[PurchaseOrderItemResponse]
    subtotal: Decimal
    total_gst: Decimal
    grand_total: Decimal
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class InventoryAlertBase(BaseModel):
    """Base inventory alert schema"""
    product_id: str
    alert_type: str  # low_stock, out_of_stock, overstock
    message: str
    is_resolved: bool = False


class InventoryAlertResponse(InventoryAlertBase):
    """Schema for inventory alert response"""
    id: str
    salon_id: str
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class InventorySummary(BaseModel):
    """Schema for inventory summary"""
    total_products: int
    total_value: Decimal
    low_stock_count: int
    out_of_stock_count: int
    pending_orders: int
    category_breakdown: dict
