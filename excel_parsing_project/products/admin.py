from django.contrib import admin
from .models import Product, ProductVariation

class ProductVariationInline(admin.TabularInline):
    model = ProductVariation
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'lowest_price', 'last_updated')
    inlines = [ProductVariationInline]

@admin.register(ProductVariation)
class ProductVariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'variation_text', 'stock')