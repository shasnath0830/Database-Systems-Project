from django.db import models

# Updated code
class User(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    user_type = models.CharField(max_length=20)
    phone = models.CharField(max_length=20, default='')


class Vehicle(models.Model):
    model = models.CharField(max_length=100)
    plate = models.CharField(max_length=20)
    status = models.CharField(max_length=20)

class Driver(models.Model):
    name = models.CharField(max_length=100)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)

class Package(models.Model):
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    shipment = models.ForeignKey('Shipment', on_delete=models.SET_NULL, null=True, related_name='packages')
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, null=True)
    description = models.TextField()
    weight = models.FloatField()
    dimensions = models.CharField(max_length=100)
    assigned_to_shipment = models.BooleanField(default=False)
    status = models.CharField(max_length=20, default='Pending')

    def save(self, *args, **kwargs):
        if not self.price:
            self.price = self.weight * 2 + (self.length * self.width * self.height) / 1000
        super().save(*args, **kwargs)

    @property
    def length(self):
        return float(self.dimensions.split('x')[0])

    @property
    def width(self):
        return float(self.dimensions.split('x')[1])

    @property
    def height(self):
        return float(self.dimensions.split('x')[2])


class Shipment(models.Model):
    order_number = models.CharField(max_length=100)
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, null=True)
    order_date = models.DateField(null=True, blank=True)
    driver = models.ForeignKey('Driver', on_delete=models.CASCADE, null=True, blank=True)
    shipment_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, default='Pending')
    total_cost = models.FloatField(default=0)
    vehicle = models.ForeignKey('Vehicle', on_delete=models.SET_NULL, null=True, blank=True)
    delivery_date = models.DateField(null=True, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
    
        if self.status == 'In Transit' and self.pk:
        # Update status of all associated packages to 'In Transit'
            self.packages.all().update(status='In Transit')
        elif self.status == 'Pending' and self.pk:
        # Update status of all associated packages to 'Pending'
            self.packages.all().update(status='Pending')
        elif self.status == 'Delivered' and self.pk:
        # Update status of all associated packages to 'Delivered'
            self.packages.all().update(status='Delivered')
    
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=200, blank=True)