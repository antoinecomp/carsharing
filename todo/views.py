from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from django.conf import settings
User = settings.AUTH_USER_MODEL
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from .forms import TodoForm
from .models import Todo
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta


def home(request):
    return render(request, 'todo/home.html')

def signupuser(request):
    if request.method == 'GET':
        return render(request, 'todo/signupuser.html', {'form':UserCreationForm()})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                db = get_user_model()
                print()
                print("request: ", request.POST.values())
                print()
                user = db.objects.create_user(request.POST['email'], request.POST['username'], 
                                            request.POST['firstname'], request.POST['company'], request.POST['mobile_number'], 
                                            password=request.POST['password1'])
                user.save()
                login(request, user)
                print("after login", request, user, request.POST['password1'])
                return redirect('currenttodos')
            except IntegrityError:
                return render(request, 'todo/signupuser.html', {'form':UserCreationForm(), 'error':'That username has already been taken. Please choose a new username'})
        else:
            return render(request, 'todo/signupuser.html', {'form':UserCreationForm(), 'error':'Passwords did not match'})

def loginuser(request):
    if request.method == 'GET':
        return render(request, 'todo/loginuser.html', {'form':AuthenticationForm()})
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        print("in login: ", request.POST['username'], request.POST['password'])
        if user is None:
            return render(request, 'todo/loginuser.html', {'form':AuthenticationForm(), 'error':'Username and password did not match'})
        else:
            login(request, user)
            return redirect('currenttodos')

@login_required
def logoutuser(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')

@login_required
def createtodo(request):
    if request.method == 'GET':
        return render(request, 'todo/createtodo.html', {'form':TodoForm()})
    else:
        try:
            form = TodoForm(request.POST)
            newtodo = form.save(commit=False)
            newtodo.user = request.user
            newtodo.save()
            return redirect('currenttodos')
        except ValueError:
            return render(request, 'todo/createtodo.html', {'form':TodoForm(), 'error':'Bad data passed in. Try again.'})

@login_required
def currenttodos(request):
    # todos = Todo.objects.filter(user=request.user, datecompleted__isnull=True)
    todos = Todo.objects.filter(datetime__gte=datetime.today())
    return render(request, 'todo/currenttodos.html', {'todos':todos})

@login_required
def completedtodos(request):
    todos = Todo.objects.filter(user=request.user, datecompleted__isnull=False).order_by('-datecompleted')
    return render(request, 'todo/completedtodos.html', {'todos':todos})

@login_required
def viewtodo(request, todo_pk):
    # todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    todo = get_object_or_404(Todo, pk=todo_pk)
    if request.user == todo.user:
        if request.method == 'GET':
            form = TodoForm(instance=todo)
            return render(request, 'todo/modifytodo.html', {'todo':todo, 'form':form})
        else:
            try:
                form = TodoForm(request.POST, instance=todo)
                form.save()
                return redirect('currenttodos')
            except ValueError:
                return render(request, 'todo/modifytodo.html', {'todo':todo, 'form':form, 'error':'Bad info'})
    else:
        if request.method == 'GET':
            form = TodoForm(instance=todo)
            return render(request, 'todo/viewtodo.html', {'todo':todo, 'form':form})


@login_required
def completetodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.datecompleted = timezone.now()
        todo.save()
        return redirect('currenttodos')

@login_required
def deletetodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo.delete()
        return redirect('currenttodos')
