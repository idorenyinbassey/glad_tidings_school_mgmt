from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from students.models import StudentProfile
from staff.models import StaffProfile
from .decorators import admin_required
import logging

# Set up logger
logger = logging.getLogger(__name__)


@login_required
def profile(request):
    user = request.user
    context = {'user': user}
    # Get the appropriate profile based on user role
    if hasattr(user, 'student_profile'):
        context['profile'] = user.student_profile
    elif hasattr(user, 'staff_profile'):
        context['profile'] = user.staff_profile

    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Update user information
                user.first_name = request.POST.get('first_name', user.first_name)
                user.last_name = request.POST.get('last_name', user.last_name)
                user.email = request.POST.get('email', user.email)
                user.save()

                # Update profile information based on role
                if hasattr(user, 'student_profile') and user.role == 'student':
                    profile = user.student_profile
                    profile.address = request.POST.get('address', profile.address)
                    profile.guardian_name = request.POST.get('guardian_name', profile.guardian_name)
                    profile.guardian_contact = request.POST.get('guardian_contact', profile.guardian_contact)
                    profile.save()
                    logger.info(f"Student profile updated for user {user.username}")

                elif hasattr(user, 'staff_profile') and user.role in ['staff', 'admin', 'it_support']:
                    profile = user.staff_profile
                    # Update staff profile fields
                    profile.position = request.POST.get('position', profile.position)
                    profile.phone = request.POST.get('phone', profile.phone)
                    profile.address = request.POST.get('address', profile.address)
                    # Record who updated the profile
                    profile.updated_by = user
                    profile.save()
                    logger.info(f"Staff profile updated for user {user.username}")

            messages.success(request, 'Profile updated successfully!')
        except Exception as e:
            logger.error(f"Error updating profile for user {user.username}: {str(e)}")
            messages.error(request, f'Error updating profile: {str(e)}')

        return redirect('profile')
    
    return render(request, 'core/profile.html', context)


# --- Admin: student/staff profile management ---

@login_required
@admin_required
def admin_students_list(request):
    students = StudentProfile.objects.select_related('user').order_by('user__last_name', 'user__first_name')
    return render(request, 'core/admin_students.html', {'students': students})


@login_required
@admin_required
def admin_student_detail(request, student_id: int):
    student = get_object_or_404(StudentProfile.objects.select_related('user'), id=student_id)
    records = getattr(student, 'attendance_records', None)
    if records is not None:
        recent_attendance = records.all().order_by('-date')[:30]
        present = recent_attendance.filter(present=True).count()
        total = recent_attendance.count()
    else:
        recent_attendance = []
        present = 0
        total = 0
    percent = round((present / total) * 100, 1) if total else 0.0
    return render(request, 'core/admin_student_detail.html', {
        'student': student,
        'recent_attendance': recent_attendance,
        'attendance_percent': percent,
    })


@login_required
@admin_required
def admin_staff_list(request):
    staff = StaffProfile.objects.select_related('user').order_by('user__last_name', 'user__first_name')
    return render(request, 'core/admin_staff.html', {'staff_list': staff})


@login_required
@admin_required
def admin_staff_detail(request, staff_id: int):
    staff = get_object_or_404(StaffProfile.objects.select_related('user'), id=staff_id)
    records = getattr(staff, 'attendance_records', None)
    if records is not None:
        recent_attendance = records.all().order_by('-date')[:30]
        present = recent_attendance.filter(present=True).count()
        total = recent_attendance.count()
    else:
        recent_attendance = []
        present = 0
        total = 0
    percent = round((present / total) * 100, 1) if total else 0.0
    return render(request, 'core/admin_staff_detail.html', {
        'staff': staff,
        'recent_attendance': recent_attendance,
        'attendance_percent': percent,
    })
