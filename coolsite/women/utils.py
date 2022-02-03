from django.db.models import Count

from women.models import *

menu = [{'title': 'О сайте', 'url_name': 'about'},
        {'title': 'Добавить статью', 'url_name': 'add_page'},
        {'title': 'Обратная связь', 'url_name': 'contact'},
        {'title': 'Войти', 'url_name': 'login'}
]

class DataMixin:
    def get_user_context(self, **kwargs):
        context = kwargs
        my_cats = Category.objects.annotate(total=Count('women')).filter(total__gt=0)

        print(len(my_cats))

        user_menu = menu.copy()
        if not self.request.user.is_authenticated:
            user_menu.pop(1)

        context['menu'] = user_menu

        context['cats'] = my_cats
        if 'cat_selected' not in context:
            context['cat_selected'] = 0
        return context