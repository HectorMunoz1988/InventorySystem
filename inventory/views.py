from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q, Sum, F
from django.utils import timezone

from .models import Product, Supplier, Category, StockMovement
from .forms import StockMovementForm


def home(request):
    low_stock_products = Product.objects.filter(
        stock__lte=F('minimum_stock')
    )

    return render(request, 'inventory/home.html', {
        'low_stock_products': low_stock_products
    })


def product_list(request):
    query = request.GET.get('q', '')
    supplier_id = request.GET.get('supplier', '')
    category_id = request.GET.get('category', '')

    products = Product.objects.all()

    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )

    if supplier_id:
        products = products.filter(
            supplier_id=supplier_id
        )

    if category_id:
        products = products.filter(
            category_id=category_id
        )

    suppliers = Supplier.objects.all()
    categories = Category.objects.all()

    return render(request, 'inventory/product_list.html', {
        'products': products,
        'suppliers': suppliers,
        'categories': categories,
        'query': query,
        'selected_supplier': supplier_id,
        'selected_category': category_id,
    })


def product_detail(request, product_id):
    product = get_object_or_404(
        Product,
        id=product_id
    )

    movements = product.movements.all().order_by('-date')

    return render(request, 'inventory/product_detail.html', {
        'product': product,
        'movements': movements,
    })


def supplier_list(request):
    suppliers = Supplier.objects.all()

    return render(request, 'inventory/supplier_list.html', {
        'suppliers': suppliers
    })


def supplier_detail(request, supplier_id):
    supplier = get_object_or_404(
        Supplier,
        id=supplier_id
    )

    products = supplier.products.all()

    return render(request, 'inventory/supplier_detail.html', {
        'supplier': supplier,
        'products': products
    })


def category_list(request):
    categories = Category.objects.all()

    return render(request, 'inventory/category_list.html', {
        'categories': categories
    })


def category_detail(request, category_id):
    category = get_object_or_404(
        Category,
        id=category_id
    )

    products = category.products.all()

    return render(request, 'inventory/category_detail.html', {
        'category': category,
        'products': products
    })


def create_movement(request, product_id):
    product = get_object_or_404(
        Product,
        id=product_id
    )

    if request.method == 'POST':
        form = StockMovementForm(request.POST)

        if form.is_valid():
            movement = form.save(commit=False)
            movement.product = product

            if movement.movement_type == 'OUT':

                if movement.quantity > product.stock:
                    messages.error(
                        request,
                        'No hay suficiente stock para realizar esta salida.'
                    )

                    return render(
                        request,
                        'inventory/movement_form.html',
                        {
                            'form': form,
                            'product': product
                        }
                    )

                product.stock -= movement.quantity

            else:
                product.stock += movement.quantity

            movement.save()
            product.save()

            messages.success(
                request,
                'Movimiento registrado correctamente.'
            )

            return redirect(
                'product_detail',
                product_id=product.id
            )

    else:
        form = StockMovementForm()

    return render(
        request,
        'inventory/movement_form.html',
        {
            'form': form,
            'product': product
        }
    )

def movement_charts(request):

    movements_by_day = (
        StockMovement.objects
        .values('date__date', 'product')
        .annotate(
            total_in=Sum(
                'quantity',
                filter=Q(movement_type='IN')
            ),
            total_out=Sum(
                'quantity',
                filter=Q(movement_type='OUT')
            )
        )
        .order_by('-date__date')
    )

    chart_data = []

    for movement in movements_by_day:

        product = Product.objects.get(
            id=movement['product']
        )

        movement_date = movement['date__date']

        total_in = movement['total_in'] or 0
        total_out = movement['total_out'] or 0

        current_stock = product.stock

        movements_after = StockMovement.objects.filter(
            product=product,
            date__date__gt=movement_date
        )

        stock_changes_after = 0

        for movement_after in movements_after:

            if movement_after.movement_type == 'IN':
                stock_changes_after += movement_after.quantity

            else:
                stock_changes_after -= movement_after.quantity

        end_of_day_stock = current_stock - stock_changes_after

        chart_data.append({
            'date': movement_date.strftime('%d/%m/%y'),
            'product': product.name,

            'entries': total_in,
            'outputs': total_out,

            'stock': end_of_day_stock,
            'minimum_stock': product.minimum_stock,

            'low_stock': end_of_day_stock <= product.minimum_stock,
        })

    return render(
        request,
        'inventory/movement_charts.html',
        {
            'chart_data': chart_data
        }
    )