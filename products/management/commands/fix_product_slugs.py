from django.core.management.base import BaseCommand
from django.utils.text import slugify
from products.models import Product

class Command(BaseCommand):
    help = 'Finds all products with empty slugs and generates a unique one for each.'

    def handle(self, *args, **options):
        products_to_fix = Product.objects.filter(slug__in=[None, ''])
        if not products_to_fix.exists():
            self.stdout.write(self.style.SUCCESS('All products already have slugs.'))
            return

        self.stdout.write(f'Found {products_to_fix.count()} products with missing slugs. Fixing now...')

        for product in products_to_fix:
            slug = slugify(product.name)
            unique_slug = slug
            num = 1
            while Product.objects.filter(slug=unique_slug).exists():
                unique_slug = f'{slug}-{num}'
                num += 1
            product.slug = unique_slug
            product.save()
            self.stdout.write(f'  - Updated slug for "{product.name}" to "{unique_slug}"')

        self.stdout.write(self.style.SUCCESS('Successfully fixed all missing product slugs.'))
