from django.core.management.base import BaseCommand
from products.models import Subcategory, Category


class Command(BaseCommand):
    help = 'Populate initial data for Category and Subcategory'

    def handle(self, *args, **kwargs):
        # Create categories
        food_category, created = Category.objects.get_or_create(name='Food')
        non_food_category, created = Category.objects.get_or_create(name='Non Food')

        # Create subcategories for Food
        food_subcategories = [
            'Вода', 'Десерт', 'Кофе', 'Крупы', 'Масло', 'Молочка', 'Мука', 'Мясо', 'Общепит', 'Овощи', 'Орехи', 'Рыба',
            'Фрукты', 'Хлеб', 'Яйца', 'Не определено'
        ]
        for subcategory_name in food_subcategories:
            Subcategory.objects.get_or_create(name=subcategory_name, category=food_category)

        # Create subcategories for Non Food
        non_food_subcategories = [
            'Авто', 'Алименты', 'Дом', 'Квартира', 'Кредит', 'Медицина', 'Одежда', 'Подарки', 'Прочее', 'Ребенок', 'Спорт',
            'Транспорт', 'Уход'
        ]
        for subcategory_name in non_food_subcategories:
            Subcategory.objects.get_or_create(name=subcategory_name, category=non_food_category)

        self.stdout.write(self.style.SUCCESS('Initial data populated successfully'))
