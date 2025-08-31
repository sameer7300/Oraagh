from django.core.management.base import BaseCommand
from django.utils.text import slugify
from products.models import Product

class Command(BaseCommand):
    help = 'Finds all products with empty or None slugs and generates a unique slug for each, forcing a save.'

    def handle(self, *args, **options):
        products_to_fix = Product.objects.filter(slug__in=[None, ''])
        count = products_to_fix.count()

        if count == 0:
            self.stdout.write(self.style.SUCCESS('All products already have valid slugs.'))
            return

        self.stdout.write(f'Found {count} products with missing slugs. Forcing fix...')

        for product in products_to_fix:
            original_name = product.name
            base_slug = slugify(product.name) or 'product' # Use 'product' if name is empty
            slug = base_slug
            num = 1
            # Ensure the generated slug is unique
            while Product.objects.filter(slug=slug).exists():
                slug = f'{base_slug}-{num}'
                num += 1
            
            product.slug = slug
            product.save()
            self.stdout.write(self.style.SUCCESS(f'  - Fixed slug for "{original_name}" -> "{slug}"'))

        self.stdout.write(self.style.SUCCESS(f'Successfully fixed {count} product slugs.'))
