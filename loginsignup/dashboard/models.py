from django.db import models
from datetime import date
from base.models import Students
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

class StudentProfile(models.Model):
    student = models.ForeignKey(Students, on_delete = models.CASCADE)

class LeaveRecord(models.Model):
    student = models.ForeignKey(Students, on_delete=models.CASCADE)
    leave_type = models.CharField(max_length = 100)
    start_date = models.DateField(default=date.today)
    end_date = models.DateField()
    reason = models.TextField()
    proof_file = models.FileField(upload_to='leave_proofs/', null=True, blank=True)
    status = models.CharField(max_length = 20, default = "Pending")
    created_at =models.DateTimeField(auto_now_add = True)
    is_approved = models.BooleanField(default=False)
    sent_on = models.DateTimeField(auto_now_add=True)
    Remarks = models.TextField(max_length=300, blank=True, null=True)
    responded_at =  models.DateTimeField(blank =True, null = True)
    

    def __str__(self):
        return f"{self.student.student_name} Leave from {self.start_date}"

class Complaint(models.Model):
    student = models.ForeignKey(
        Students, 
        on_delete=models.SET_NULL,   # change this
        null=True,                   # allow NULL in DB
        blank=True                   # allow empty in form
    )
    student_class = models.CharField(max_length=50, default="")
    section = models.CharField(max_length=5, default="")
    is_anonymous = models.BooleanField(default=False)
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=100)
    description = models.TextField()
    status = models.CharField(max_length=20, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)
    Remarks = models.TextField(max_length=300, blank=True, null=True) 
    responded_at =  models.DateTimeField(blank =True, null = True)

    def __str__(self):
        if self.student:
            return f"{self.title} - {self.student.student_name}"
        return f"{self.title} - Anonymous"
    



@login_required(login_url='login')
def teacher_dashboard(request):
    # Ensure the user actually has a teacher profile to avoid errors
    try:
        teacher = request.user.teacher
    except AttributeError:
        # Redirect or show error if a student/admin tries to access this
        return redirect('login')

    complaints = Complaint.objects.filter(
        student_class=teacher.student_class,
        section=teacher.section,
        status__in=["Pending", "In Progress"]
    ).order_by("-created_at")

    return render(request, "dashboard/teacher_home.html", {
        "teacher": teacher, 
        "complaints": complaints
    })


@login_required
def update_complaint_status(request, id):
    if request.method == "POST":
        complaint = Complaint.objects.get(id=id)
        complaint.status = request.POST.get("status")
        complaint.save()
    return redirect('dashboard:teacher_home')



    




    