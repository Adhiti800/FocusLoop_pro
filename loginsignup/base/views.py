import re
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import Teacher, Students
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile
from .forms import RegistrationForm

# ===========================
# Welcome Pages
# ===========================
def welcome(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')  # unified dashboard router
    return render(request, 'welcome.html')


# ===========================
# Student Signup
# ===========================
def student_signup_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "User created successfully.")
            # Create student profile
             
            login(request, user)
            return redirect('base:student_info')  # student fills additional info
  
    else:
        form = RegistrationForm()
    return render(request, 'registration/student_signup.html', {"form": form})


# ===========================
# Teacher Signup
# ===========================
def teacher_signup_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create teacher profile

            login(request, user)
            return redirect('base:teacher_info')  # teacher fills additional info
        else:
            print(form.errors)
            messages.error(request, "Signup failed. Please fix the errores.")
            
    else:
        form = RegistrationForm()
    return render(request, 'registration/teacher_signup.html', {"form": form})


# ===========================
# Student Info
# ===========================

def student_info(request):
    if request.method == "POST":
        student_name = request.POST.get("student_name")
        roll_number=request.POST.get("roll_number")
      
        if not re.match(r'^[a-zA-Z\s]+$', student_name):
            messages.error(request, "Student name cannot contain numbers or special characters.")
            return redirect('base:student_info')
        
        if Students.objects.filter(roll_number=roll_number).exists():
            messages.error(request, "This Roll Number already exists.")
            return redirect('base:student_info')

        Students.objects.create(
            user=request.user,
            student_name=request.POST.get("student_name"),
            roll_number=request.POST.get("roll_number"),
            student_class=request.POST.get("student_class"),
            section=request.POST.get("section"),
        )
        return redirect("base:login")
    
    return render(request, "student_info.html")



# ===========================
# Teacher Info
# ===========================

def teacher_info(request):
    if request.method == "POST":
        teacher_name = request.POST.get("teacher_name")
        teacher_id = request.POST.get("teacher_id")
      
        if not re.match(r'^[a-zA-Z\s]+$', teacher_name):
            messages.error(request, "Teacher name cannot contain numbers or special characters.")
            return redirect('base:teacher_info')
        
        if Teacher.objects.filter(teacher_id=teacher_id).exists():
            messages.error(request, "This Teacher ID already exists.")
            return redirect('base:teacher_info')


        Teacher.objects.create(
            user=request.user,
            teacher_name=request.POST.get("teacher_name"),
            teacher_id = request.POST.get("teacher_id"),
            your_subject=request.POST.get("your_subject"),
            student_class=request.POST.get("class_assigned"),
            section=request.POST.get("section"),
        )
        return redirect("base:login")  # sends teacher to their dashboard
    return render(request, "teacher_info.html")


# ===========================
# Login View
# ===========================
def login_view(request):
   if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            if user.role == 'student':
                return redirect("dashboard:student_home")
            elif user.role == 'teacher':
                return redirect("dashboard:teacher_home")
        return render(request, "login.html") 

# ===========================
# Logout View
# ===========================
def logout_view(request):
    logout(request)
    return redirect('base:welcome')


#==========================

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
