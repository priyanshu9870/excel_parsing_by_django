import logging
from django.shortcuts import render, redirect
import openpyxl
from .models import Product, ProductVariation
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.db import IntegrityError

# Set up logging
logger = logging.getLogger(__name__)

def upload_products(request):
    if request.method == 'POST' and request.FILES['excel_file']:
        excel_file = request.FILES['excel_file']
        if excel_file.name.endswith('.xlsx') or excel_file.name.endswith('.xls'):
            fs = FileSystemStorage()
            file_path = fs.save(excel_file.name, excel_file)
            wb = openpyxl.load_workbook(fs.path(file_path))
            ws = wb.active

            for index, row in enumerate(ws.iter_rows(min_row=2), start=2):
                if len(row) < 4:
                    logger.error(f"Row {index} error: The row has fewer than 4 columns. Data: {row}")
                    continue  # Skip this row

                product_name = row[0].value
                variation_text = row[1].value
                stock = row[2].value
                lowest_price = row[3].value

                logger.debug(f"Row {index}: Product Name={product_name}, Variation={variation_text}, Stock={stock}, Lowest Price={lowest_price}")

                # Check if lowest_price is None
                if lowest_price is None:
                    logger.error(f"Row {index} error: lowest_price is None for product '{product_name}'")
                    continue  # Skip this row

                # Check if lowest_price can be converted to a float
                try:
                    lowest_price = float(lowest_price)
                except (ValueError, TypeError) as e:
                    logger.error(f"Row {index} error: Invalid lowest_price '{lowest_price}' for product '{product_name}' - {str(e)}")
                    continue  # Skip this row

                # Ensure lowest_price is not being set to None accidentally
                logger.debug(f"Row {index}: Converted lowest_price={lowest_price}")

                try:
                    product, created = Product.objects.get_or_create(name=product_name)
                    if not created:
                        product.lowest_price = min(product.lowest_price, lowest_price)
                    else:
                        product.lowest_price = lowest_price
                    product.save()

                    ProductVariation.objects.update_or_create(
                        product=product,
                        variation_text=variation_text,
                        defaults={'stock': stock}
                    )
                except IntegrityError as e:
                    logger.error(f"Row {index} error: IntegrityError occurred - {str(e)}")
                    continue  # Skip this row on error
                except Exception as e:
                    logger.error(f"Row {index} error: Unexpected error occurred - {str(e)}")
                    continue  # Skip this row on error

            return redirect('product_listing_page')

    return render(request, 'upload_products.html')

def product_listing(request):
    products = Product.objects.all().values('id', 'name', 'lowest_price', 'last_updated')
    response_data = []

    for product in products:
        variations = list(ProductVariation.objects.filter(product_id=product['id']).values('variation_text', 'stock'))
        product_data = {
            'name': product['name'],
            'lowest_price': product['lowest_price'],
            'last_updated': product['last_updated'],
            'variations': variations
        }
        response_data.append(product_data)

    return JsonResponse(response_data, safe=False)

def product_listing_page(request):
    return render(request, 'product_listing.html')