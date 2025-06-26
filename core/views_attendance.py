from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from students.models import AttendanceRecord
from staff.models import StaffAttendance

@login_required
def attendance(request):
    user = request.user
    if hasattr(user, 'student_profile'):
        records = AttendanceRecord.objects.filter(student=user.student_profile)
        return render(request, 'core/attendance_student.html', {'records': records})
    elif hasattr(user, 'staff_profile'):
        records = StaffAttendance.objects.filter(staff=user.staff_profile)
        return render(request, 'core/attendance_staff.html', {'records': records})
    else:
        return render(request, 'core/attendance_admin.html')
