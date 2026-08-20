from django.contrib import admin

from .models import Supplier, Category, Product, StockMovement


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'email',
        'phone',
    )

    search_fields = (
        'name',
        'email',
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'name',
    )

    search_fields = (
        'name',
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'category',
        'supplier',
        'stock',
        'minimum_stock',
        'stock_status',
    )

    list_filter = (
        'category',
        'supplier',
    )

    search_fields = (
        'name',
        'supplier__name',
        'category__name',
    )

    def stock_status(self, obj):
        if obj.stock <= obj.minimum_stock:
            return 'Stock bajo'

        return 'Stock suficiente'

    stock_status.short_description = 'Estado del stock'


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = (
        'product',
        'movement_type',
        'quantity',
        'date',
    )

    list_filter = (
        'movement_type',
        'product',
    )

    search_fields = (
        'product__name',
    )

    ordering = (
        '-date',
    )