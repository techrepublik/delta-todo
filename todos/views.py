from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, authenticate
from django.db.models import Q
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required

from .models import ToDo
from .forms import ToDoForm


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('todo_list')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('todo_list')
        else:
            error_message = 'Invalid credentials'
    else:
        error_message = ''
    return render(request, 'login.html', {'error_message': error_message})


@login_required
def todo_list(request):
    query = request.GET.get('search', '')
    if query:
        todos = ToDo.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query), user=request.user
        )
    else:
        todos = ToDo.objects.filter(user=request.user)
        # todos = ToDo.objects.all()

    return render(request, 'todo_list.html', {'todos': todos, 'query': query})


@login_required
def todo_create(request):
    if request.method == 'POST':
        form = ToDoForm(request.POST)
        if form.is_valid():
            todo = form.save(commit=False)
            todo.user = request.user
            todo.save()
            return redirect('todo_list')
    else:
        form = ToDoForm()
    return render(request, 'todo_form.html', {'form': form})


def todo_update(request, pk):
    todo = get_object_or_404(ToDo, pk=pk)
    if request.method == 'POST':
        form = ToDoForm(request.POST, instance=todo)
        if form.is_valid():
            form.save()
            return redirect('todo_list')
    else:
        form = ToDoForm(instance=todo)
    return render(request, 'todo_form.html', {'form': form})


def todo_delete(request, pk):
    todo = get_object_or_404(ToDo, pk=pk)
    if request.method == 'POST':
        todo.delete()
        return redirect('todo_list')
    return render(request, 'todo_confirm_delete.html', {'todo': todo})
