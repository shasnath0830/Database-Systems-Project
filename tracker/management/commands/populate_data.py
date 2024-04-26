from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker
from tracker.models import User, Customer, Package, Shipment, Driver, Vehicle
import random
import string

class Command(BaseCommand):
    help = 'Populates the database with mock data'

    @transaction.atomic
    def handle(self, *args, **options):
        fake = Faker()

        # Delete all data
        Customer.objects.all().delete()
        User.objects.all().delete()
        Package.objects.all().delete()
        Shipment.objects.all().delete()
        Driver.objects.all().delete()
        Vehicle.objects.all().delete()

        # List of package descriptions
        package_descriptions = [
            'Wireless Bluetooth Earbuds', 'Instant Pot Electric Pressure Cooker', 'Echo Dot Smart Speaker',
            'Kindle Paperwhite E-reader', 'Fire TV Stick 4K', 'Fitbit Versa 2 Smartwatch',
            'Bose QuietComfort 35 II Wireless Headphones', 'iRobot Roomba Robot Vacuum', 'Cuisinart Coffee Maker',
            'Philips Sonicare Electric Toothbrush', 'Anker PowerCore Portable Charger',
            'Hydro Flask Stainless Steel Water Bottle', 'Instant Read Meat Thermometer', 'Keurig K-Classic Coffee Maker',
            'Samsung 4K Ultra HD Smart TV', 'Sony PlayStation 5 Console', 'Nintendo Switch Gaming Console',
            'Apple iPad Air', 'Microsoft Surface Laptop', 'Logitech Wireless Mouse', 'Crucial SSD Internal Hard Drive',
            'SanDisk Ultra 128GB MicroSD Card', 'Seagate Portable External Hard Drive', 'HP OfficeJet Wireless Printer',
            'Brother Laser Printer', 'Epson EcoTank Wireless Printer', 'Canon EOS Rebel DSLR Camera',
            'GoPro HERO9 Black Action Camera', 'Fujifilm Instax Mini Instant Camera', 'Ring Video Doorbell',
            'Arlo Pro Security Camera System', 'Nest Learning Thermostat', 'Philips Hue Smart Light Bulbs',
            'iHealth No-Touch Forehead Thermometer', 'Oral-B Pro Electric Toothbrush', 'Waterpik Water Flosser',
            'Braun Electric Shaver', 'Philips Norelco Multigroom Trimmer', 'Conair Hair Dryer',
            'Revlon One-Step Hair Dryer & Volumizer', 'CHI Ceramic Hair Straightener', 'Tresemme Keratin Smooth Shampoo',
            'Olaplex Hair Perfector No. 3', 'CeraVe Daily Moisturizing Lotion', 'Neutrogena Ultra Sheer Sunscreen',
            'Maybelline New York Mascara', 'L\'Oreal Paris Revitalift Anti-Aging Cream',
            'Crest 3D White Professional Effects Whitestrips', 'Listerine Cool Mint Antiseptic Mouthwash'
        ]

        # Create 20 new user accounts
        for _ in range(20):
            # Generate a random first and last name
            first_name = fake.first_name()
            last_name = fake.last_name()

            # Generate a random email that complies with the email regex
            email = f"{first_name.lower()}.{last_name.lower()}@{fake.domain_name()}"

            # Create a user with the signup form
            user = User.objects.create(
                email=email,
                password='password',
                user_type='customer',
                phone=fake.phone_number()
            )
            customer = Customer.objects.create(
                user=user,
                first_name=first_name,
                last_name=last_name,
                address=fake.address()
            )

            # Create packages for the customer
            num_packages = random.randint(5, 15)
            for _ in range(num_packages):
                # Generate package details
                description = random.choice(package_descriptions)
                weight = random.choice([random.randint(1, 20), round(random.uniform(1, 20), 2)])
                length = random.choice([random.randint(3, 20), round(random.uniform(3, 20), 2)])
                width = random.choice([random.randint(3, 20), round(random.uniform(3, 20), 2)])
                height = random.choice([random.randint(3, 20), round(random.uniform(3, 20), 2)])
                dimensions = f"{length}x{width}x{height}"

                # Create the package
                Package.objects.create(
                    customer=customer,
                    description=description,
                    weight=weight,
                    dimensions=dimensions,
                    status='Pending'
                )

        self.stdout.write(self.style.SUCCESS('Mock data populated successfully.'))