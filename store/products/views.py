from django.shortcuts import render, HttpResponse, HttpResponseRedirect, redirect, get_object_or_404
from products.models import *
from products.forms import *
from django.contrib import auth
from django.urls import reverse
from django.contrib.auth import logout


# Create your views here.
def home(request):
    if request.method == 'POST':
        print('ok')
        form = BookingForm(request.POST)
        if form.is_valid():

            # Обработка данных формы
            checkin = form.cleaned_data['checkin']
            checkout = form.cleaned_data['checkout']
            room_type = form.cleaned_data['room_type']
            rooms = form.cleaned_data['rooms']

            # Сохраняем данные формы в сессии для передачи в index4
            request.session['checkin'] = checkin.strftime('%Y-%m-%d')
            request.session['checkout'] = checkout.strftime('%Y-%m-%d')
            request.session['room_type'] = room_type
            request.session['rooms'] = rooms
            return redirect('index4')
        else:
            print(form.errors)
    else:
        form = BookingForm()       
    return render(request, 'products/index.html',{'form': form})

def about(request):
    context = {
        'title': 'FOUR SEASON - about'
    }
    return render(request,'products/index2.html', context)

def profile(request): #функция изменения профиля
    if request.method == 'POST': #Проверка  метода запроса 
        form = UserProfileForm(instance=request.user, data=request.POST) #создание объекты формы с данными
        if form.is_valid(): #проверка вводимых данных
            form.save() #сохранение измененных данных
            return HttpResponseRedirect(reverse('index3')) 
    else:
        form = UserProfileForm(instance=request.user) 
    context = {
        'title': 'FOUR SEASON - profile',
        'form' : form
    }
    return render(request,'products/index3.html', context) #отображение шаблона с данными

def custom_logout(request): #функция выхода из аккаунта
    logout(request) #выход из аккаунта
    return redirect('index')

def administration(request):
    return 



def catalog(request):
    from django.db.models import Q
    from datetime import datetime

    checkin = request.session.get('checkin')
    checkout = request.session.get('checkout')
    room_type = request.session.get('room_type')
    rooms = request.session.get('rooms')

    if not (checkin and checkout and room_type and rooms):
        return render(request, 'products/index4.html', {'numbers': []})

    checkin_date = datetime.strptime(checkin, '%Y-%m-%d')
    checkout_date = datetime.strptime(checkout, '%Y-%m-%d')

    numbers = hotel_number.objects.filter(
        characteristics_id__type=room_type,
        characteristics_id__number_of_rooms=rooms
    ).exclude(
        Q(reservation__start_date__lt=checkout_date) & Q(reservation__end_date__gt=checkin_date)
    )

    numbers_data = [{'id': number.id, 'image': number.image.url, 'characteristics': number.characteristics_id} for number in numbers]

    context = {
        'title': 'CATALOG',
        'numbers': numbers_data,
    }

    return render(request, 'products/index4.html', context)




def reservation_number(request, number_id):
    from datetime import datetime   

    number = get_object_or_404(hotel_number, id=number_id)

    checkin = request.session.get('checkin')
    checkout = request.session.get('checkout')
    room_type = request.session.get('room_type')
    number_of_rooms = request.session.get('number_of_rooms')

    # Преобразование дат из строкового формата в объекты даты
    checkin_date = datetime.strptime(checkin, '%Y-%m-%d')
    checkout_date = datetime.strptime(checkout, '%Y-%m-%d')
    nights = (checkout_date - checkin_date).days
    total_price = nights * number.characteristics_id.price

    if request.method == 'POST':
        # Сохранение данных бронирования
        new_reservation = reservation(
            hotel_number_id=number,
            guest_id=request.user,
            start_date=checkin_date,
            end_date=checkout_date,
            total_price=total_price,
            date=datetime.now()
        )
        new_reservation.save()

        return redirect('reservation_successfully')

    context = {
        'title': 'FOUR SEASON - reservation',
        'number': number,
        'form': reservation()  # Placeholder form; это просто для передачи csrf_token
    }
    return render(request, 'products/index5.html', context)

def reservation_successfully(request):
    context = {
        'title': 'FOUR SEASON'
    }
    return render(request, 'products/index6.html', context)



def authorization(request): #функция авторизации(входа в аккаунт) пользователя
    if request.method == 'POST': #Проверка  метода запроса 
        form = UserLoginForm(data=request.POST) #создание объекты формы с данными
        if form.is_valid(): #проверка вводимых данных
            username = form.cleaned_data['username'] 
            password = form.cleaned_data['password']
            user = auth.authenticate(username=username, password=password) #проверка аутентификации
            if user is not None:
                auth.login(request, user) #вход в систему 
                return HttpResponseRedirect(reverse('index')) #Перенос на страницу входа
    else:
        form = UserLoginForm() #создание пустой формы
    context = {
        'title': 'FOUR SEASON - authorization',
        'form': form
    }
    return render(request, 'products/index7.html', context) #отображение шаблона с данными


def registration(request): #функция регистрации пользователя
    if request.method == 'POST':   #Проверка  метода запроса 
        form = UserRegistrationForm(data=request.POST) #создание объекты формы с данными
        if form.is_valid(): #проверка вводимых данных
            form.save() #Сохранение данных в БД
            return HttpResponseRedirect(reverse('index7')) #Перенос на страницу входа
    else:
        form = UserRegistrationForm() #создание пустой формы
    context = {
        'title': 'FOUR SEASON - registration',
        'form': form,
    }
    return render(request,'products/index8.html', context) #отображение шаблона с данными

def booking_view(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            checkin = form.cleaned_data['start_date']
            checkout = form.cleaned_data['end_date']
            type = form.cleaned_data['type']
            number_of_rooms = form.cleaned_data['number_of_rooms']
            request.session['checkin'] = checkin.strftime('%Y-%m-%d')
            request.session['checkout'] = checkout.strftime('%Y-%m-%d')
            request.session['room_type'] = type
            request.session['rooms'] = number_of_rooms
            return redirect('catalog')  # Перенаправление к каталогу после успешного ввода данных
    else:
        form = BookingForm()
    
    return render(request, 'index.html', {'form': form})

