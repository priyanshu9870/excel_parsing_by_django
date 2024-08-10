from django.urls import path
from .views import product_listing, product_listing_page, upload_products

urlpatterns = [
    path('products/', product_listing, name='product_listing'),
    path('', product_listing_page, name='product_listing_page'),
    path('upload-products/', upload_products, name='upload_products'),
]