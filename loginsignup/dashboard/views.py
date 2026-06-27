import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from base.models import Students
from .models import Complaint, LeaveRecord
from django.contrib import messages
from datetime import date
from django.db.models import Q



# ------------------------------
# Dashboard router: redirect based on role
# ------------------------------

def dashboard_router(request):
    user = request.user

    if hasattr(user, 'teacher'):
        return redirect('dashboard:teacher_home')

    if hasattr(user, 'student'):
        return redirect('dashboard:student_home')

    return redirect('login')  # or 'home', etc.
 

# ------------------------------
# Student home/dashboard
# ------------------------------
def student_home_view(request):
    student = request.user.student

    leave_count = LeaveRecord.objects.filter(student=student).count()
    ownership_filter = (
        Q(student=student) | 
        Q(student=None, student_class=student.student_class, section=student.section)
    )

    complaints = Complaint.objects.filter(ownership_filter).exclude(status="Resolved").order_by("-created_at")
    
   
    complaint_count = complaints.count() # Use the filtered queryset count

    return render(request, 'dashboard/student_home.html', {
        "student": student,
        "leave_count": leave_count,
        "complaint_count": complaint_count,
        "complaints": complaints,
    })



# ------------------------------
# Teacher home/dashboard
# ------------------------------
def teacher_home_view(request):
    teacher = request.user.teacher
    
    # 1. The Base Queryset (All complaints for this teacher's scope)
    # Use this for the table to show history.
    all_teacher_complaints = Complaint.objects.filter(
        student_class=teacher.student_class,
        section=teacher.section
    ).order_by("-created_at")

    # 2. The Filtered Count (Excluding Resolved)
    # This is what shows up in your dashboard "Stats Card"
    active_complaint_count = all_teacher_complaints.exclude(status="Resolved").count()

    # 3. Leave Records (Only Pending/Active if preferred)
    leaves_qs = LeaveRecord.objects.filter(
        student__student_class=teacher.student_class,
        student__section=teacher.section
    )
    # Optional: exclude(status="Approved") if you only want to count pending leaves
    active_leave_count = leaves_qs.exclude(status="Approved").count() 

    return render(request, 'dashboard/teacher_home.html', {
        "teacher": teacher,
        "leave_count": active_leave_count,
        "complaint_count": active_complaint_count,
        "complaints": all_teacher_complaints, # Shows everything (Pending, In Progress, Resolved)
    })

# ------------------------------
# Student complaints
# ------------------------------
@login_required(login_url='login')
def student_complain_view(request):
    student = request.user.student

    if request.method == 'POST':
        complaint_title = request.POST.get('complaint_title')
        complaint_category = request.POST.get('complaint_category')
   
        
        if not re.match(r'^[a-zA-Z\s]+$', complaint_title) or not re.match(r'^[a-zA-Z\s]+$', complaint_category):
            messages.error(request, "Complaint title and category cannot contain numbers or special characters.")
            return redirect('dashboard:student_complain')
        

        Complaint.objects.create(
            student=student,
            is_anonymous= (request.POST.get("anonymous") == "on"),
            title=complaint_title,
            student_class= student.student_class,
            section = student.section,
            category=complaint_category,
            description=request.POST.get('complaint_detail') or '',
            status='Pending',
            Remarks='',  # Initialize remarks as empty
        )

        return redirect('dashboard:student_complain')


    complaints = Complaint.objects.filter(student=student).order_by("-created_at")

    return render(request, 'dashboard/student_complain.html', {
        'student': student,
        'complaints': complaints,
    })



# ------------------------------
# Student leave requests
# ------------------------------


@login_required(login_url='login')
def student_leave_view(request):
    student = request.user.student

    if request.method == 'POST':
        leave_type = request.POST.get("leave_type")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")

        errors = []

 
        if not re.match(r'^[a-zA-Z\s]+$', leave_type or ""):
            errors.append("Leave type cannot contain numbers or special characters.")

      
        if start_date and end_date:
            if start_date > end_date:
                errors.append("Start date cannot be after end date.")

        today = date.today().isoformat()

        if start_date and start_date < today:
            errors.append("Start date cannot be in the past.")

        if end_date and end_date < today:
            errors.append("End date cannot be in the past.")

        if errors:
            for error in errors:
                messages.error(request, error)

            return redirect('dashboard:student_leave')

        
        LeaveRecord.objects.create(
            student=student,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            reason=request.POST.get("reason"),
            proof_file=request.FILES.get("proof_file"),
            status="Pending"
        )

        return redirect('dashboard:student_leave')

    leave_applications = LeaveRecord.objects.filter(student=student).order_by("-created_at")

    return render(request, 'dashboard/student_leave.html', {
        "student": student,
        "leave_applications": leave_applications
    })


# ------------------------------
# Teacher: update complaint status
# ------------------------------
@login_required(login_url='login')
def update_complaint_status(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id)

    if request.method == "POST":    
        new_status = request.POST.get("status")
        if new_status in ["Pending", "In Progress", "Resolved"]:
            complaint.status = new_status
            complaint.save()
        
        Remarks = request.POST.get("Remarks")
        complaint.Remarks= Remarks
        complaint.responded_at = date.today()
        complaint.save()

        return redirect('dashboard:teacher_complain')
    
    return render(request, 'dashboard/teacher_complain.html', {"complaint": complaint}) 


#------------------------------
# Teacher: leave applications view
#------------------------------
@login_required
def teacher_leave_view(request):
    teacher = request.user.teacher
    # Filter leave applications for students in the teacher's class
    leave_applications = LeaveRecord.objects.filter(
        student__student_class=teacher.student_class,
        student__section=teacher.section
    ).order_by('-created_at')
    
    return render(request, 'dashboard/teacher_leave.html', {
        'teacher': teacher,
        'leave_applications': leave_applications
    })

#-------------------------------
# Updating Leave Status
#-------------------------------
@login_required
def update_leave_status(request, leave_id):
    leave = get_object_or_404(LeaveRecord, id=leave_id)
    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status in ["Approved", "Rejected"]:
            leave.status = new_status
            leave.save()
        
        Remarks = request.POST.get("Remarks")
        leave.Remarks = Remarks
        leave.responded_at = date.today()
        leave.save()
    return redirect('dashboard:teacher_leave_requests')



#------------------------------
# Teacher: Complaint view
#------------------------------
@login_required
def teacher_complain_view(request):
    teacher = request.user.teacher     
    complaints = Complaint.objects.filter(
        student_class=teacher.student_class,
        section=teacher.section
    ).filter(
        status__in=["Pending", "In Progress"]
    ).order_by("-created_at")

    return render(request, 'dashboard/teacher_complain.html', {
        'complaints': complaints,
        'teacher': teacher,
         'teacher_id': teacher.teacher_id,
        'section': teacher.section,
        'class_assigned': teacher.student_class,
    })

   

#-------------------------------
#Teacher Profile View
#-------------------------------
def teacher_profile_view(request):
    teacher = request.user.teacher
    return render(request, 'dashboard/teacher_profile.html',{
        'teacher': teacher,
        'section': teacher.section,
        'class_assigned': teacher.student_class,
        'subject': teacher.your_subject,
 })

#-------------------------------
#Student Profile View
#-------------------------------
def student_profile_view(request):
    student = request.user.student
    return render(request, 'dashboard/student_profile.html',{
        'student': student,
        'class': student.student_class,
        'section':student.section,
        'roll_number': student.roll_number,

    }
 )

#-------------------------------
#Replacing Files in Leave Application
#-------------------------------
@login_required
def delete_leave_file(request, leave_id):
    student = Students.objects.get(user=request.user)
    leave = LeaveRecord.objects.filter(student=student)
    if leave.proof_file:
        leave.proof_file.delete(save=False)
        leave.proof_file = None
        leave.save()
        return redirect('dashboard:student_leave')
    
@login_required
def replace_leave_file(request, leave_id):
    
    leave = LeaveRecord.objects.get(id=leave_id, student__user=request.user)
    if request.method == "POST":
        new_file = request.FILES.get("proof_file")
        if new_file:
            if leave.proof_file:
                leave.proof_file.delete(save=False)  # Delete old file
        leave.proof_file = new_file  # Assign new file
        leave.save()
    return redirect('dashboard:student_leave')