from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.views import LoginView
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseNotFound, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DeleteView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import *
from .forms import *
from .utils import *


menu = [{'title': 'О сайте', 'url_name': 'about'},
        {'title': 'Добавить статью', 'url_name': 'add_page'},
        {'title': 'Обратная связь', 'url_name': 'contact'},
        {'title': 'Войти', 'url_name': 'login'}
]


def index(request):
    posts = Women.objects.all()
    context = {'posts': posts,
               'menu': menu,
               'title': 'Главная страница',
               'cat_selected': 0}
    return render(request, 'women/index.html', context=context)

"""Класс-представление для отображения данных на главной странице, заменяет функцию index"""
class WomenHome(DataMixin, ListView):
    # ListView автоматически передаёт paginator и page_obj
    model = Women
    template_name = 'women/index.html' # по умолчанию ищется women_list.html
    context_object_name = 'posts'# по умолчанию ищется object_list
    # extra_context = {'title': 'Главная страница'} # c помощью параметра extra-context можно передавать только статические(неизменяемые) объекты, поэтому создадим функцию для динамических

    """ Метод формирует и статический и динамический контекст """
    def get_context_data(self, *, object_list=None, **kwargs):
        #получить контекст, который уже сформирован для шаблона
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title="Главная страница")
        return dict(list(context.items()) + list(c_def.items()))

    """Метод определяет данные, выбранные из модели"""
    def get_queryset(self):
        return Women.objects.filter(is_published=True).select_related('cat')

def about(request):
    contact_list = Women.objects.all()
    paginator = Paginator(contact_list, 3)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'women/about.html', {'page_obj': page_obj, 'menu': menu, 'title': 'О сайте'})

"""Класс-представление для добавления поста, заменяет функцию addpage"""
class AddPage(LoginRequiredMixin, DataMixin, CreateView):
    # указывает на класс формы, который будет связан с классом-представлением
    form_class = AddPostForm
    template_name = 'women/addpage.html'
    # reverse - создает маршрут в момент создания класса
    # reverse_lazy - создает маршрут, когда он нужен становится
    success_url = reverse_lazy('home')
    login_url = reverse_lazy('home')
    raise_exception = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title="Добавление статьи")
        return dict(list(context.items()) + list(c_def.items()))



def addpage(request):
    if request.method == "POST":
        form = AddPostForm(request.POST, request.FILES) # список файлов которые были переданы из формы на сервер
        if form.is_valid():
            # try:
                # Women.objects.create(**form.cleaned_data)
            form.save()
            return redirect('home')
            # except:
            #     form.add_error(None, 'Ошибка добавления поста')
    else:
        form = AddPostForm()
    return render(request, 'women/addpage.html', {'form': form, 'menu': menu, 'title': 'Добавление статьи'})


def contact(request):
    return HttpResponse("Page for contacting")


# def login(request):
#     return HttpResponse("Page for login")


def show_post(request, post_slug):
    post = get_object_or_404(Women, slug=post_slug)

    context = {
        'post': post,
        'menu': menu,
        'title': post.title,
        'cat_selected': post.cat_id
    }
    return render(request, 'women/post.html', context=context)

"""Класс-представление для отображения поста, заменяет функцию show_post"""
class ShowPost(DataMixin, DeleteView):
    model = Women
    template_name = 'women/post.html'
    slug_url_kwarg = 'post_slug' #по умолчанию берётся 'slug'. Для id - pk_url_kwarg = 'post_pk' - по умолчанию 'pk'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title=context['post'])
        return dict(list(context.items()) + list(c_def.items()))

"""Класс-представление для отображения данных по категориям, заменяет функцию show_post"""
class WomenCategory(DataMixin, ListView):
    model = Women
    template_name = 'women/index.html'
    context_object_name = 'posts'
    allow_empty = False

    """Отбирает аргументы маршрутра по self.kwargs. Благодаря __ идет в таблицу, указанную ссылкой в основной и там берет поле slug"""
    def get_queryset(self):
        return Women.objects.filter(cat__slug=self.kwargs['cat_slug'], is_published=True).select_related('cat')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c = Category.objects.get(slug=self.kwargs['cat_slug'])
        c_def = self.get_user_context(title='Категория - ' + str(c.name),
                                                                 cat_selected=c.pk)
        return dict(list(context.items()) + list(c_def.items()))


def show_category(request, cat_slug):
    # posts = Women.objects.filter(cat__slug=cat_slug)
    posts = Women.objects.filter(cat_id=Category.objects.filter(slug=cat_slug)[0].id)


    if len(posts) == 0:
        raise Http404

    context = {'posts': posts,
               'menu': menu,
               'title': 'Главная страница',
               'cat_selected': cat_slug}
    return render(request, 'women/index.html', context=context)

class RegisterUser(DataMixin, CreateView):
    # form_class = UserCreationForm
    form_class = RegisterUserForm
    template_name = 'women/register.html'
    success_url = reverse_lazy('login')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Регистрация')
        return dict(list(context.items()) + list(c_def.items()))

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('home')

class LoginUser(DataMixin, LoginView):
    # form_class = AuthenticationForm
    form_class = LoginUserForm
    template_name = 'women/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Авторизация')
        return {**context, **c_def}

    def get_success_url(self):
        return reverse_lazy('home')

def logout_user(request):
    logout(request)
    return redirect('login')

def categories(request, catid):
    print(request.GET)
    if catid == 1:
        return redirect('home')
    return HttpResponse(f"<h1>Women application categories</h1><p>{catid}<p>")


def pageNotFound(request, exception):
    return HttpResponseNotFound("<h1>Page not found<h1>")

