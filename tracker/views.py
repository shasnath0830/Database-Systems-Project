from django.shortcuts import render, redirect
from django.contrib import messages
from .models import User, Vehicle, Driver, Package, Shipment, Customer
from django.utils import timezone
from datetime import date
import random
import string
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.db.models import Count
from django.http import HttpResponse
from graphviz import Digraph
import seaborn as sns
import matplotlib.pyplot as plt
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.shortcuts import render
from .models import Package, Shipment
import io
import base64
import pandas as pd
from django.db.models.functions import TruncDate
from datetime import datetime
from django.db.models import Count, F, DateField
from django.shortcuts import render
import pandas as pd
import matplotlib
matplotlib.use('Agg')
from django.apps import apps
from django.db import connection
from django.shortcuts import render, redirect
from django.http import JsonResponse
import webbrowser
from datetime import date
from django.db.models import Avg
from django.http import HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from decimal import Decimal


def advanced_feature(request):
    status_counts = Package.objects.values('status').annotate(count=Count('id'))
    status_df = pd.DataFrame(list(status_counts))

    shipments = Shipment.objects.values('order_date').annotate(count=Count('id'))
    shipments_df = pd.DataFrame(list(shipments))
    if 'order_date' in shipments_df.columns:
        shipments_df['order_date'] = pd.to_datetime(shipments_df['order_date']).dt.date
        trend_df = shipments_df.groupby('order_date').sum().reset_index()
    else:
        trend_df = pd.DataFrame(columns=['order_date', 'count'])

    weights = Package.objects.values_list('weight', flat=True)
    weight_df = pd.DataFrame({'weight': weights})

    delivery_times = Shipment.objects.annotate(delivery_time=F('delivery_date') - F('order_date')).values_list('delivery_time', flat=True)
    delivery_time_df = pd.DataFrame({'delivery_time': delivery_times})

    plots = []

    plt.figure(figsize=(8, 6))
    sns.countplot(x='status', data=status_df)
    plt.title('Package Status Distribution')
    plt.xlabel('Status')
    plt.ylabel('Count')
    plot_buffer = io.BytesIO()
    plt.savefig(plot_buffer, format='png')
    plot_buffer.seek(0)
    plot_base64 = base64.b64encode(plot_buffer.read()).decode('utf-8')
    plots.append(plot_base64)
    plt.close()

    if not trend_df.empty:
        plt.figure(figsize=(10, 6))
        sns.lineplot(x='order_date', y='count', data=trend_df)
        plt.title('Shipment Trend Analysis')
        plt.xlabel('Order Date')
        plt.ylabel('Shipment Count')
        plt.xticks(rotation=45)
        plot_buffer = io.BytesIO()
        plt.savefig(plot_buffer, format='png')
        plot_buffer.seek(0)
        plot_base64 = base64.b64encode(plot_buffer.read()).decode('utf-8')
        plots.append(plot_base64)
        plt.close()
    else:
        plots.append(None)

    plt.figure(figsize=(8, 6))
    sns.histplot(data=weight_df, x='weight', kde=True)
    plt.title('Package Weight Distribution')
    plt.xlabel('Weight')
    plt.ylabel('Frequency')
    plot_buffer = io.BytesIO()
    plt.savefig(plot_buffer, format='png')
    plot_buffer.seek(0)
    plot_base64 = base64.b64encode(plot_buffer.read()).decode('utf-8')
    plots.append(plot_base64)
    plt.close()

    plt.figure(figsize=(8, 6))
    sns.boxplot(data=delivery_time_df, x='delivery_time')
    plt.title('Delivery Time Analysis')
    plt.xlabel('Delivery Time (Days)')
    plot_buffer = io.BytesIO()
    plt.savefig(plot_buffer, format='png')
    plot_buffer.seek(0)
    plot_base64 = base64.b64encode(plot_buffer.read()).decode('utf-8')
    plots.append(plot_base64)
    plt.close()

    package_customer_counts = Package.objects.values('customer').annotate(count=Count('id'))
    package_customer_df = pd.DataFrame(list(package_customer_counts))
    plt.figure(figsize=(10, 6))
    sns.barplot(x='customer', y='count', data=package_customer_df)
    plt.title('Package Distribution by Customer')
    plt.xlabel('Customer')
    plt.ylabel('Number of Packages')
    plt.xticks(rotation=45)
    plot_buffer = io.BytesIO()
    plt.savefig(plot_buffer, format='png')
    plot_buffer.seek(0)
    plot_base64 = base64.b64encode(plot_buffer.read()).decode('utf-8')
    plots.append(plot_base64)
    plt.close()

    shipment_cost_volume_data = Shipment.objects.values('total_cost').annotate(volume=F('packages__weight') * 0.01)
    total_costs = [data['total_cost'] for data in shipment_cost_volume_data]
    volumes = [data['volume'] for data in shipment_cost_volume_data]

    plt.figure(figsize=(8, 6))
    plt.scatter(total_costs, volumes)
    plt.title('Shipment Cost vs Volume')
    plt.xlabel('Total Cost')
    plt.ylabel('Volume')
    plot_buffer = io.BytesIO()
    plt.savefig(plot_buffer, format='png')
    plot_buffer.seek(0)
    plot_base64 = base64.b64encode(plot_buffer.read()).decode('utf-8')
    plots.append(plot_base64)
    plt.close()

    context = {
        'plots': plots,
    }

    return render(request, 'advanced_feature.html', context)



def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = User.objects.filter(email=email, password=password).first()
        if user:
            request.session['email'] = email
            if user.user_type == 'customer':
                return redirect('customer')
            elif user.user_type == 'admin':
                return redirect('admin_dashboard')
        else:
            messages.error(request, 'Invalid email or password.')
    
    # Clear existing messages before rendering the login page
    storage = messages.get_messages(request)
    storage.used = True
    
    return render(request, 'index.html')


@login_required
def visualization(request):
    # Generate the database schema diagram
    graph = Digraph(format='svg')
    
    # Add nodes for each table
    for table_name in connection.introspection.table_names():
        graph.node(table_name, table_name)
    
    # Add edges for foreign key relationships
    for table_name in connection.introspection.table_names():
        for row in connection.introspection.get_constraints(table_name).values():
            if row['foreign_key']:
                graph.edge(table_name, row['foreign_key'][0])
    
    # Add record count and other information as node labels
    for table_name in connection.introspection.table_names():
        model = connection.introspection.get_table_description(connection.cursor(), table_name)
        model_class = model.model_class()
        if model_class:
            record_count = model_class.objects.aggregate(count=Count('pk'))['count']
            label = f"{table_name}\nRecords: {record_count}"
            graph.node(table_name, label=label)
    
    # Render the diagram as an SVG
    diagram_svg = graph.pipe(format='svg').decode('utf-8')
    
    return render(request, 'visualization.html', {'diagram_svg': diagram_svg})


def signup(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirmPassword')
        user_type = request.POST.get('userType')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists. Please use a different email.')
            return render(request, 'signup.html')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'signup.html')

        user = User.objects.create(email=email, password=password, user_type=user_type)

        if user_type == 'customer':
            first_name = request.POST.get('firstName', '')
            last_name = request.POST.get('lastName', '')
            address = request.POST.get('address', '')
            Customer.objects.create(user=user, first_name=first_name, last_name=last_name, address=address)
            messages.success(request, 'Customer account created successfully. Please login.')
        else:
            messages.success(request, 'Admin account created successfully. Please login.')

        return redirect('login')

    return render(request, 'signup.html')


def update_package(request, package_id):
    package = get_object_or_404(Package, id=package_id)
    if request.method == 'POST':
        description = request.POST.get('description')
        weight = request.POST.get('weight')
        dimensions = request.POST.get('dimensions')

        package.description = description
        package.weight = Decimal(weight) if weight else package.weight
        package.dimensions = dimensions

        package.save()
        messages.success(request, 'Package updated successfully.')
        return redirect('customer')

    return render(request, 'update_package.html', {'package': package})


def delete_shipment(request, shipment_id):
    try:
        shipment = Shipment.objects.get(id=shipment_id)
    except Shipment.DoesNotExist:
        messages.error(request, 'Shipment not found.')
        return redirect('some_error_handling_view')

    # Get the vehicle assigned to the shipment
    vehicle = shipment.vehicle

    # Set the vehicle status to 'Available' if it exists
    if vehicle:
        vehicle.status = 'Available'
        vehicle.save()

    # Update status of associated packages if any
    packages = shipment.package_set.all()
    for package in packages:
        package.status = 'Pending'
        package.assigned_to_shipment = False
        package.save()

    # Delete the shipment
    shipment.delete()

    messages.success(request, 'Shipment deleted successfully.')
    return redirect('admin_dashboard')




def update_driver(request, driver_id):
    try:
        driver = Driver.objects.get(id=driver_id)
    except Driver.DoesNotExist:
        messages.error(request, 'Driver not found.')
        return redirect('some_error_handling_view')

    vehicles = Vehicle.objects.all()

    if request.method == 'POST':
        vehicle_id = request.POST.get('vehicleId')

        if vehicle_id:
            try:
                vehicle = Vehicle.objects.get(id=vehicle_id)
                driver.vehicle = vehicle
                driver.save()
                messages.success(request, 'Driver updated successfully.')
                return redirect('admin_dashboard')
            except Vehicle.DoesNotExist:
                messages.error(request, 'Vehicle not found.')
                return redirect('some_error_handling_view')
        else:
            driver.vehicle = None
            driver.save()
            messages.success(request, 'Driver updated successfully.')
            return redirect('admin_dashboard')

    return render(request, 'update_driver.html', {'driver': driver, 'vehicles': vehicles})

def delete_driver(request, driver_id):
    if request.method == 'POST':
        Driver.objects.filter(id=driver_id).delete()
        messages.success(request, 'Driver deleted successfully.')
    return redirect('admin_dashboard')

def update_vehicle(request, vehicle_id):
    vehicle = Vehicle.objects.get(id=vehicle_id)
    if request.method == 'POST':
        model = request.POST.get('model')
        plate = request.POST.get('plate')
        status = request.POST.get('status')

        # Check if the vehicle is currently assigned to any shipment
        assigned_shipments = Shipment.objects.filter(vehicle=vehicle)
        if not assigned_shipments:  # If no shipments are assigned
            vehicle.model = model
            vehicle.plate = plate
            vehicle.status = status
            vehicle.save()
            messages.success(request, 'Vehicle updated successfully.')
        else:
            messages.error(request, 'Cannot update vehicle status. It is currently assigned to a shipment.')

        return redirect('admin_dashboard')
    return render(request, 'update_vehicle.html', {'vehicle': vehicle})

def delete_vehicle(request, vehicle_id):
    if request.method == 'POST':
        Vehicle.objects.filter(id=vehicle_id).delete()
        messages.success(request, 'Vehicle deleted successfully.')
    return redirect('admin_dashboard')

def update_shipment(request, shipment_id):
    shipment = Shipment.objects.get(id=shipment_id)
    drivers = Driver.objects.all()
    customers = Customer.objects.all()
    vehicles = Vehicle.objects.all()

    if request.method == 'POST':
        # Retrieve form data
        # Other form fields...
        vehicle_id = request.POST.get('vehicleId')

        with transaction.atomic():
            try:
                # Update shipment fields
                # Other fields...
                if vehicle_id:
                    vehicle = Vehicle.objects.get(id=vehicle_id)
                    shipment.vehicle = vehicle
                else:
                    shipment.vehicle = None

                # Save the updated shipment
                shipment.save()

                messages.success(request, 'Shipment updated successfully.')
                return redirect('admin_dashboard')
            except (Customer.DoesNotExist, Driver.DoesNotExist, Vehicle.DoesNotExist) as e:
                messages.error(request, str(e))
                # Rollback the transaction and display the update shipment page with error messages
                transaction.set_rollback(True)

    return render(request, 'update_shipment.html', {'shipment': shipment, 'drivers': drivers, 'customers': customers, 'vehicles': vehicles})


def update_shipment_status(request, shipment_id):
    if request.method == 'POST':
        shipment = get_object_or_404(Shipment, id=shipment_id)
        status = request.POST.get('status')

        if status == 'Delivered':
            if shipment.status == 'In Transit':
                # Update shipment status and delivery date
                shipment.status = status
                shipment.delivery_date = timezone.now().date()
                shipment.save()

                # Update packages status to Delivered
                for package in shipment.packages.all():
                    package.status = 'Delivered'
                    package.save()

                messages.success(request, 'Shipment status updated successfully.')
            else:
                messages.error(request, 'Invalid status transition.')
        elif status == 'In Transit':
            # Update shipment status to In Transit
            shipment.status = status
            shipment.save()

            # Update packages status to In Transit
            for package in shipment.packages.all():
                package.status = 'In Transit'
                package.save()

            messages.success(request, 'Shipment status updated successfully.')
        else:
            # Update shipment status
            shipment.status = status
            shipment.save()
            messages.success(request, 'Shipment status updated successfully.')

    return redirect('admin_dashboard')

def logout(request):
    request.session.flush()
    messages.success(request, 'Logged out successfully.')
    storage = messages.get_messages(request)
    storage.used = True
    return redirect('login')


def customer(request):
    if 'email' not in request.session:
        messages.error(request, 'Please login to access the customer dashboard.')
        return redirect('login')

    customer_email = request.session['email']
    customer = Customer.objects.filter(user__email=customer_email).first()
    if not customer:
        messages.error(request, 'Customer not found.')
        return redirect('login')

    if request.method == 'POST':
        description = request.POST.get('description', '')
        weight = float(request.POST.get('weight', 0))
        length = float(request.POST.get('length', 0))
        width = float(request.POST.get('width', 0))
        height = float(request.POST.get('height', 0))
        dimensions = f"{length}x{width}x{height}"
        
        price = request.POST.get('price', '0')  # Default to '0' if not provided
        try:
            price = Decimal(price)
        except InvalidOperation:
            messages.error(request, "Invalid price format.")
            return redirect('customer')
        Package.objects.create(
            shipment=None,
            customer=customer,  # Set the customer field
            description=description,
            weight=weight,
            dimensions=dimensions,
            status='Pending',
            # price = price
        )
        messages.success(request, 'Package created successfully.')
        return redirect('customer')

    packages = Package.objects.filter(customer=customer).select_related('shipment').order_by('id')
    shipments = Shipment.objects.filter(customer=customer)
    context = {
        'packages': packages,
        'shipments': shipments,
        'customer': customer,
    }
    return render(request, 'customer.html', context)

def calculate_price(weight, length, width, height):
    base_price = 10.0
    volume = length * width * height
    price = base_price + (weight * 0.5) + (volume * 0.1)
    return round(price, 2)

def admin(request):
    if 'email' not in request.session:
        messages.error(request, 'Please login to access the admin dashboard.')
        return redirect('login')

    user_email = request.session['email']
    user = User.objects.filter(email=user_email, user_type='admin').first()
    if not user:
        messages.error(request, 'Access denied. You are not an admin.')
        return redirect('login')

    return redirect('admin_dashboard')

def admin_dashboard(request):
    if 'email' not in request.session:
        messages.error(request, 'Please login to access the admin dashboard.')
        return redirect('login')

    user_email = request.session['email']
    user = User.objects.filter(email=user_email, user_type='admin').first()
    if not user:
        messages.error(request, 'Access denied. You are not an admin.')
        return redirect('login')

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'assign_package':
            package_id = request.POST.get('packageId')
            shipment_id = request.POST.get('shipmentId')
            package = Package.objects.get(id=package_id)
            shipment = Shipment.objects.get(id=shipment_id)
            package.shipment = shipment
            package.save()
            messages.success(request, 'Package assigned to shipment successfully.')
        elif action == 'assign_driver':
            driver_id = request.POST.get('driverId')
            vehicle_id = request.POST.get('vehicleId')
            
            # Check if the vehicle is already assigned to another driver
            try:
                existing_assignment = Driver.objects.get(vehicle_id=vehicle_id)
                if existing_assignment.id != int(driver_id):
                    messages.error(request, 'The selected vehicle is already assigned to another driver.')
                    return redirect('admin_dashboard')
            except Driver.DoesNotExist:
                pass  # No existing assignment, proceed with the assignment

            # Proceed with the assignment
            return update_driver(request, driver_id)
        elif action == 'assign_shipment':
            shipment_id = request.POST.get('shipmentId')
            vehicle_id = request.POST.get('vehicleId')
            try:
                shipment = Shipment.objects.get(id=shipment_id)
                vehicle = Vehicle.objects.get(id=vehicle_id)

                if vehicle.status == 'Available':
                    # Set the previous vehicle status to "Available" if it was assigned
                    if shipment.vehicle:
                        previous_vehicle = shipment.vehicle
                        previous_vehicle.status = 'Available'
                        previous_vehicle.save()

                    # Update the shipment's vehicle and set the new vehicle status to "Assigned"
                    shipment.vehicle = vehicle
                    shipment.save()
                    vehicle.status = 'Assigned'
                    vehicle.save()

                    messages.success(request, 'Shipment assigned to vehicle successfully.')
                else:
                    messages.error(request, 'The selected vehicle is not available.')
            except Shipment.DoesNotExist:
                messages.error(request, 'Selected shipment not found.')
            except Vehicle.DoesNotExist:
                messages.error(request, 'Selected vehicle not found.')
        elif action == 'mark_delivered':
            package_id = request.POST.get('packageId')
            package = Package.objects.get(id=package_id)
            package.status = 'Delivered'
            package.save()
            messages.success(request, 'Package marked as delivered successfully.')

    packages = Package.objects.all()
    shipments = Shipment.objects.all()
    drivers = Driver.objects.all()
    vehicles = Vehicle.objects.all()
    context = {
        'packages': packages,
        'shipments': shipments,
        'drivers': drivers,
        'vehicles': vehicles,
    }
    return render(request, 'admin_dashboard.html', context)


def create_driver(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        vehicle_id = request.POST.get('vehicleId')
        vehicle = Vehicle.objects.get(id=vehicle_id)
        Driver.objects.create(name=name, vehicle=vehicle)
        messages.success(request, 'Driver created successfully.')
    return redirect('admin_dashboard')

def create_vehicle(request):
    if request.method == 'POST':
        model = request.POST.get('model')
        plate = request.POST.get('plate')
        status = request.POST.get('status')
        Vehicle.objects.create(model=model, plate=plate, status=status)
        messages.success(request, 'Vehicle created successfully.')
    return redirect('admin_dashboard')

def generate_order_number():
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(10))



from django.shortcuts import get_object_or_404

def assign_package(request):
    if request.method == 'POST':
        package_ids = request.POST.getlist('packageId')
        shipment_id = request.POST.get('shipmentId')

        if shipment_id:
            shipment = get_object_or_404(Shipment, id=shipment_id)
        else:
            order_number = generate_order_number()
            shipment = Shipment.objects.create(
                order_number=order_number,
                order_date=date.today(),
                driver=None,
                shipment_date=date.today(),
                total_cost=0.0,
                delivery_date=None,  # Set delivery_date to None initially
                status='Pending'  # Set the initial status to 'Pending'
            )

        total_cost = Decimal('0.00') 

        for package_id in package_ids:
            try:
                package = Package.objects.get(id=package_id)

                price_str = request.POST.get(f'packagePrice_{package_id}', '0.00')
                clean_price_str = ''.join(char for char in price_str if char.isdigit() or char == '.')

                try:
                     package_price = Decimal(clean_price_str)
                except decimal.ConversionSyntax:
                     messages.error(request, f'Invalid price format for package {package_id}.')
                     continue

                package.price = package_price
                package.shipment = shipment
                package.assigned_to_shipment = True
                package.status = 'In Transit'  # Change the status to 'In Transit'
                package.save()

                total_cost += package_price
            except Package.DoesNotExist:
                pass

        Shipment.objects.filter(id=shipment.id).update(total_cost=F('total_cost') + total_cost)

        messages.success(request, 'Packages assigned to shipment successfully.')
        return redirect('admin_dashboard')

    return HttpResponseNotAllowed(['POST'])

def delete_package(request, package_id):
    if request.method == 'POST':
        # Use the 'package_id' from the function argument, not from POST data
        Package.objects.filter(id=package_id).delete()
        messages.success(request, 'Package deleted successfully.')
    return redirect('customer')

    
def search_database(request):
    if request.method == 'POST':
        query = request.POST.get('query')
        result = None
        error = None
        success_message = None

        try:
            with connection.cursor() as cursor:
                # Execute the SQL query
                cursor.execute(query)

                if query.upper().startswith('SELECT'):
                    # Fetch the results if it's a SELECT query
                    columns = [col[0] for col in cursor.description]
                    result = [dict(zip(columns, row)) for row in cursor.fetchall()]
                else:
                    # Get the number of affected rows for non-SELECT queries
                    rows_affected = cursor.rowcount
                    if query.upper().startswith('UPDATE'):
                        success_message = f"{rows_affected} records updated successfully."
                    elif query.upper().startswith('DELETE'):
                        success_message = f"{rows_affected} records deleted successfully."
                    elif query.upper().startswith('INSERT'):
                        success_message = f"{rows_affected} records inserted successfully."
                    else:
                        success_message = "Query executed successfully."

        except Exception as e:
            error = str(e)

        context = {
            'query': query,
            'result': result,
            'error': error,
            'success_message': success_message,
            'packages': Package.objects.all(),
            'shipments': Shipment.objects.all(),
            'drivers': Driver.objects.all(),
            'vehicles': Vehicle.objects.all(),
            'active_view': 'showdb',
        }
        return render(request, 'admin_dashboard.html', context)

    context = {
        'packages': Package.objects.all(),
        'shipments': Shipment.objects.all(),
        'drivers': Driver.objects.all(),
        'vehicles': Vehicle.objects.all(),
        'active_view': 'showdb',
    }
    return render(request, 'admin_dashboard.html', context)

def assign_package(request):
    if request.method == 'POST':
        package_ids = request.POST.getlist('packageId')
        shipment_id = request.POST.get('shipmentId')

        if shipment_id:
            shipment = get_object_or_404(Shipment, id=shipment_id)
        else:
            order_number = generate_order_number()
            shipment = Shipment.objects.create(
                order_number=order_number,
                order_date=date.today(),
                driver=None,
                shipment_date=date.today(),
                total_cost=0.0,
                delivery_date=date.today()
            )

        total_cost = Decimal('0.00')

        for package_id in package_ids:
            try:
                package = Package.objects.get(id=package_id)

                price_str = request.POST.get(f'packagePrice_{package_id}', '0.00')
                clean_price_str = ''.join(char for char in price_str if char.isdigit() or char == '.')

                try:
                    package_price = Decimal(clean_price_str)
                except decimal.ConversionSyntax:
                    messages.error(request, f'Invalid price format for package {package_id}.')
                    continue

                package.price = package_price
                package.shipment = shipment
                package.assigned_to_shipment = True
                package.save()

                total_cost += package_price
            except Package.DoesNotExist:
                pass

        Shipment.objects.filter(id=shipment.id).update(total_cost=F('total_cost') + total_cost)

        messages.success(request, 'Packages assigned to shipment successfully.')
        return redirect('admin_dashboard')

    return HttpResponseNotAllowed(['POST'])
