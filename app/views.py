from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login,logout,authenticate
from forms.createform import TodoForm
from .models import Todo
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db import IntegrityError


def home(request):
    user=request.user
    return render(request,"home.html",{"username":user})

def login_view(request):
    if request.method=="POST":
        user=authenticate(username=request.POST["username"],password=request.POST["password"])
        if user is not None:
            login(request,user)
            return redirect("home")
        else:
            return render(request, "login.html", {"error": "Invalid username or password.","form":AuthenticationForm()})
    else:
        return render(request,"login.html",{"form":AuthenticationForm()})

@login_required
def logout_view(request):
    if request.method=="POST":
        logout(request)
    return render(request,"logout.html")


def singup(request):
    if request.method=="POST":
        if request.POST["password1"]==request.POST["password2"]:    # checking for both password are correct or not
            try:
                user=User.objects.create_user(username=request.POST["username"],password=request.POST["password1"])   # create new user
                user.save()
                user=authenticate(username=request.POST["username"],password=request.POST["password1"])   # newly user authenticate and login
                login(request,user)
                return redirect("main")
            except IntegrityError:
                return render(request,"singup.html",{"form":UserCreationForm(),"error":"The username is alredy taken please choose another one"})

        else:
            return render(request,"singup.html",{"form":UserCreationForm,"error":"password does not match"})   # if password and confirm password does not match 
    else:
        return render(request,"singup.html",{"form":UserCreationForm()})   # to show the singup form

def main(request):
    username=request.user  # get the username 
    context={"username":username}
    return render(request,"main.html",context)

@login_required
def create(request):
    form = TodoForm()
    context = {"form": form}
    if request.method == "POST":
        try:
            form = TodoForm(request.POST)
            new = form.save(commit=False)
            new.user = request.user
            new.save()
            return redirect("home")
        except ValueError:
            return render(request,"create.html",{"form":form,"error":"Bad data inseted"})
    else:
        return render(request, "create.html", context)

@login_required
def list(request):
    data=Todo.objects.filter(user=request.user,Datecompleted__isnull=True)
    context={"data":data}
    return render(request,"list.html",context)

@login_required
def update_read(request, pk):
    data = get_object_or_404(Todo, pk=pk, user=request.user)
    if request.method == 'GET':
        form = TodoForm(instance=data)
        return render(request, 'update_read.html', {'data':data, 'form':form})
    else:
        try:
            form = TodoForm(request.POST, instance=data)
            form.save()
            return redirect('list')
        except ValueError:
            return render(request, 'update_read.html', {'data':data, 'form':form, 'error':'Bad info'})


@login_required
def delete(request, pk):
    data = get_object_or_404(Todo, pk=pk, user=request.user)
    if request.method == 'POST':
        data.delete()
        return redirect('list')

@login_required
def completed(request):
    data = Todo.objects.filter(user=request.user, Datecompleted__isnull=False)
    return render(request, 'completed.html', {'data':data})


@login_required
def completetodo(request, pk):
    data = get_object_or_404(Todo, pk=pk, user=request.user)
    if request.method == 'POST':
        data.Datecompleted = timezone.now()
        data.save()
        return redirect('list')






