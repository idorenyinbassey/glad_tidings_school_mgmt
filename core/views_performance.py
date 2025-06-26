from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from students.models import AcademicStatus, AttendanceRecord
from staff.models import StudentPerformance
from assignments.models import Submission
from cbt.models import CBTSession

@login_required
def performance_analytics(request):
    user = request.user
    context = {}
    if hasattr(user, 'student_profile'):
        student = user.student_profile
        context['academic_statuses'] = AcademicStatus.objects.filter(student=student)
        context['attendance_records'] = AttendanceRecord.objects.filter(student=student)
        context['performances'] = StudentPerformance.objects.filter(student=student)
        context['submissions'] = Submission.objects.filter(student=student)
        context['cbt_sessions'] = CBTSession.objects.filter(student=student)
        return render(request, 'core/performance_student.html', context)
    elif hasattr(user, 'staff_profile'):
        staff = user.staff_profile
        context['performances'] = StudentPerformance.objects.filter(staff=staff)
        context['taught_classes'] = staff.timetables.all()
        return render(request, 'core/performance_staff.html', context)
    else:
        return render(request, 'core/performance_admin.html', context)
