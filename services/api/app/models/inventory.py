"""Inventory Management Models"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from app.models.base import FirestoreBase, TimestampMixin
from app.schemas.inventory import (
    ProductCategory, StockStatus, StockTransactionType, PurchaseOrderStatus
)


class Product(FirestoreBase):
    """Product model for inventory management"""
    collection_name = "products"
    id_field = "product_id"
    
    def __init__(self, **data):
        super().__init__(**data)
        self.name: str = data.get("name", "")
        self.sku: str = data.get("sku", "")
        self.salon_id: str = data.get("salon_id", "")
        self.category: str = data.get("category", ProductCategory.OTHER.value)
        self.description: Optional[str] = data.get("description")
        self.unit: str = data.get("unit", "piece")
        self.unit_price: Decimal = Decimal(str(data.get("unit_price", 0)))
        self.cost_price: Decimal = Decimal(str(data.get("cost_price", 0)))
        self.gst_rate: Decimal = Decimal(str(data.get("gst_rate", "18.00")))
        self.hsn_code: Optional[str] = data.get("hsn_code")
        self.current_quantity: int = data.get("current_quantity", 0)
        self.min_stock_level: int = data.get("min_stock_level", 5)
        self.max_stock_level: int = data.get("max_stock_level", 100)
        self.reorder_point: int = data.get("reorder_point", 10)
        self.stock_status: str = data.get("stock_status", StockStatus.IN_STOCK.value)
        self.last_restocked_at: Optional[datetime] = data.get("last_restocked_at")
        self.is_active: bool = data.get("is_active", True)
        self.created_at: datetime = data.get("created_at", datetime.utcnow())
        self.updated_at: datetime = data.get("updated_at", datetime.utcnow())
    
    def update_stock_status(self) -> str:
        """Update stock status based on current quantity"""
        if self.current_quantity <= 0:
            self.stock_status = StockStatus.OUT_OF_STOCK.value
        elif self.current_quantity <= self.reorder_point:
            self.stock_status = StockStatus.LOW_STOCK.value
        else:
            self.stock_status = StockStatus.IN_STOCK.value
        return self.stock_status
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "product_id": self.product_id,
            "name": self.name,
            "sku": self.sku,
            "salon_id": self.salon_id,
            "category": self.category,
            "description": self.description,
            "unit": self.unit,
            "unit_price": float(self.unit_price),
            "cost_price": float(self.cost_price),
            "gst_rate": float(self.gst_rate),
            "hsn_code": self.hsn_code,
            "current_quantity": self.current_quantity,
            "min_stock_level": self.min_stock_level,
            "max_stock_level": self.max_stock_level,
            "reorder_point": self.reorder_point,
            "stock_status": self.stock_status,
            "last_restocked_at": self.last_restocked_at.isoformat() if self.last_restocked_at else None,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class StockTransaction(FirestoreBase):
    """Stock transaction model for tracking inventory movements"""
    collection_name = "stock_transactions"
    id_field = "transaction_id"
    
    def __init__(self, **data):
        super().__init__(**data)
        self.product_id: str = data.get("product_id", "")
        self.salon_id: str = data.get("salon_id", "")
        self.transaction_type: str = data.get("transaction_type", StockTransactionType.PURCHASE.value)
        self.quantity: int = data.get("quantity", 0)
        self.previous_quantity: int = data.get("previous_quantity", 0)
        self.new_quantity: int = data.get("new_quantity", 0)
        self.unit_price: Optional[Decimal] = data.get("unit_price") and Decimal(str(data.get("unit_price")))
        self.total_value: Decimal = Decimal(str(data.get("total_value", 0)))
        self.reference_type: Optional[str] = data.get("reference_type")
        self.reference_id: Optional[str] = data.get("reference_id")
        self.notes: Optional[str] = data.get("notes")
        self.created_by: Optional[str] = data.get("created_by")
        self.created_at: datetime = data.get("created_at", datetime.utcnow())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "transaction_id": self.transaction_id,
            "product_id": self.product_id,
            "salon_id": self.salon_id,
            "transaction_type": self.transaction_type,
            "quantity": self.quantity,
            "previous_quantity": self.previous_quantity,
            "new_quantity": self.new_quantity,
            "unit_price": float(self.unit_price) if self.unit_price else None,
            "total_value": float(self.total_value),
            "reference_type": self.reference_type,
            "reference_id": self.reference_id,
            "notes": self.notes,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class PurchaseOrderItem:
    """Purchase order item model"""
    def __init__(self, **data):
        self.id: str = data.get("id", "")
        self.product_id: str = data.get("product_id", "")
        self.product_name: str = data.get("product_name", "")
        self.product_sku: str = data.get("product_sku", "")
        self.quantity: int = data.get("quantity", 0)
        self.unit_price: Decimal = Decimal(str(data.get("unit_price", 0)))
        self.gst_rate: Decimal = Decimal(str(data.get("gst_rate", "18.00")))
        self.subtotal: Decimal = Decimal(str(data.get("subtotal", 0)))
        self.gst_amount: Decimal = Decimal(str(data.get("gst_amount", 0)))
        self.total: Decimal = Decimal(str(data.get("total", 0)))
    
    def calculate_totals(self):
        """Calculate subtotal, GST, and total"""
        self.subtotal = self.quantity * self.unit_price
        self.gst_amount = self.subtotal * (self.gst_rate / 100)
        self.total = self.subtotal + self.gst_amount
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "product_id": self.product_id,
            "product_name": self.product_name,
            "product_sku": self.product_sku,
            "quantity": self.quantity,
            "unit_price": float(self.unit_price),
            "gst_rate": float(self.gst_rate),
            "subtotal": float(self.subtotal),
            "gst_amount": float(self.gst_amount),
            "total": float(self.total),
        }


class PurchaseOrder(FirestoreBase):
    """Purchase order model for inventory procurement"""
    collection_name = "purchase_orders"
    id_field = "order_id"
    
    def __init__(self, **data):
        super().__init__(**data)
        self.order_number: str = data.get("order_number", "")
        self.salon_id: str = data.get("salon_id", "")
        self.supplier_name: str = data.get("supplier_name", "")
        self.supplier_gstin: Optional[str] = data.get("supplier_gstin")
        self.supplier_address: Optional[str] = data.get("supplier_address")
        self.supplier_phone: Optional[str] = data.get("supplier_phone")
        self.status: str = data.get("status", PurchaseOrderStatus.DRAFT.value)
        self.items: List[Dict] = data.get("items", [])
        self.subtotal: Decimal = Decimal(str(data.get("subtotal", 0)))
        self.total_gst: Decimal = Decimal(str(data.get("total_gst", 0)))
        self.grand_total: Decimal = Decimal(str(data.get("grand_total", 0)))
        self.expected_delivery_date: Optional[datetime] = data.get("expected_delivery_date")
        self.notes: Optional[str] = data.get("notes")
        self.created_by: Optional[str] = data.get("created_by")
        self.created_at: datetime = data.get("created_at", datetime.utcnow())
        self.updated_at: datetime = data.get("updated_at", datetime.utcnow())
    
    def calculate_totals(self):
        """Calculate order totals from items"""
        self.subtotal = Decimal("0")
        self.total_gst = Decimal("0")
        for item_data in self.items:
            item = PurchaseOrderItem(**item_data)
            item.calculate_totals()
            self.subtotal += item.subtotal
            self.total_gst += item.gst_amount
        self.grand_total = self.subtotal + self.total_gst
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "order_id": self.order_id,
            "order_number": self.order_number,
            "salon_id": self.salon_id,
            "supplier_name": self.supplier_name,
            "supplier_gstin": self.supplier_gstin,
            "supplier_address": self.supplier_address,
            "supplier_phone": self.supplier_phone,
            "status": self.status,
            "items": self.items,
            "subtotal": float(self.subtotal),
            "total_gst": float(self.total_gst),
            "grand_total": float(self.grand_total),
            "expected_delivery_date": self.expected_delivery_date.isoformat() if self.expected_delivery_date else None,
            "notes": self.notes,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class InventoryAlert(FirestoreBase):
    """Inventory alert model for low stock notifications"""
    collection_name = "inventory_alerts"
    id_field = "alert_id"
    
    def __init__(self, **data):
        super().__init__(**data)
        self.product_id: str = data.get("product_id", "")
        self.salon_id: str = data.get("salon_id", "")
        self.alert_type: str = data.get("alert_type", "low_stock")
        self.message: str = data.get("message", "")
        self.is_resolved: bool = data.get("is_resolved", False)
        self.resolved_by: Optional[str] = data.get("resolved_by")
        self.resolved_at: Optional[datetime] = data.get("resolved_at")
        self.created_at: datetime = data.get("created_at", datetime.utcnow())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "alert_id": self.alert_id,
            "product_id": self.product_id,
            "salon_id": self.salon_id,
            "alert_type": self.alert_type,
            "message": self.message,
            "is_resolved": self.is_resolved,
            "resolved_by": self.resolved_by,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
