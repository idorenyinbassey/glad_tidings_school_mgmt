from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from datetime import datetime
from staff.models import StaffAttendance, StaffProfile
from students.models import AttendanceRecord as StudentAttendance, StudentProfile
from django.db.models import Q
from .decorators import admin_required, role_required


@login_required
def attendance(request):
    user = request.user
    # Admin overview first (takes precedence)
    is_admin = (getattr(user, 'role', None) == 'admin') or user.is_superuser
    if is_admin and not hasattr(user, 'student_profile') and not hasattr(user, 'staff_profile'):
        start_date = request.GET.get('start_date') or ''
        end_date = request.GET.get('end_date') or ''
        today = timezone.now().date()

        student_qs = StudentAttendance.objects.all()
        staff_qs = StaffAttendance.objects.all()

        if start_date:
            try:
                student_qs = student_qs.filter(date__gte=start_date)
                staff_qs = staff_qs.filter(date__gte=start_date)
            except Exception:
                messages.warning(request, 'Invalid start date filter ignored.')
        if end_date:
            try:
                student_qs = student_qs.filter(date__lte=end_date)
                staff_qs = staff_qs.filter(date__lte=end_date)
            except Exception:
                messages.warning(request, 'Invalid end date filter ignored.')

        # Aggregates
        student_total = student_qs.count()
        student_present = student_qs.filter(present=True).count()
        student_absent = student_qs.filter(present=False).count()
        student_percent = round((student_present / student_total) * 100, 1) if student_total else 0.0

        staff_total = staff_qs.count()
        staff_present = staff_qs.filter(present=True).count()
        staff_absent = staff_qs.filter(present=False).count()
        staff_percent = round((staff_present / staff_total) * 100, 1) if staff_total else 0.0

        # Today snapshot
        students_today_present = StudentAttendance.objects.filter(date=today, present=True).count()
        staff_today_present = StaffAttendance.objects.filter(date=today, present=True).count()

        context = {
            'start_date': start_date,
            'end_date': end_date,
            'today': today,
            # Students
            'student_total': student_total,
            'student_present': student_present,
            'student_absent': student_absent,
            'student_percent': student_percent,
            'student_records': student_qs.select_related('student__user').order_by('-date')[:50],
            # Staff
            'staff_total': staff_total,
            'staff_present': staff_present,
            'staff_absent': staff_absent,
            'staff_percent': staff_percent,
            'staff_records': staff_qs.select_related('staff__user').order_by('-date')[:50],
            # Today
            'students_today_present': students_today_present,
            'staff_today_present': staff_today_present,
        }
        return render(request, 'core/attendance_admin.html', context)
    # Student: filterable list + stats
    if hasattr(user, 'student_profile'):
        student = user.student_profile
        start_date = request.GET.get('start_date') or ''
        end_date = request.GET.get('end_date') or ''

        records = student.attendance_records.all().order_by('-date')  # pyright: ignore[reportAttributeAccessIssue]
        if start_date:
            try:
                records = records.filter(date__gte=start_date)
            except Exception:
                messages.warning(request, 'Invalid start date filter ignored.')
        if end_date:
            try:
                records = records.filter(date__lte=end_date)
            except Exception:
                messages.warning(request, 'Invalid end date filter ignored.')

        total = records.count()
        present = records.filter(present=True).count()
        absent = records.filter(present=False).count()
        percent = round((present / total) * 100, 1) if total else 0.0

        context = {
            'records': records,
            'total_days': total,
            'days_present': present,
            'days_absent': absent,
            'attendance_percent': percent,
            'start_date': start_date,
            'end_date': end_date,
        }
        return render(request, 'core/attendance_student.html', context)

    # Staff: filterable list + mark today present/absent
    if hasattr(user, 'staff_profile'):
        staff = user.staff_profile

        if request.method == 'POST':
            action = request.POST.get('action')  # 'present' | 'absent'
            date_str = request.POST.get('date')
            try:
                mark_date = (
                    datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else timezone.now().date()
                )
            except Exception:
                mark_date = timezone.now().date()

            obj, _ = StaffAttendance.objects.get_or_create(
                staff=staff,
                date=mark_date,
                defaults={'present': True, 'created_by': user},
            )
            if action == 'present':
                obj.present = True
            elif action == 'absent':
                obj.present = False
            if obj.created_by is None:
                obj.created_by = user
            obj.save()
            messages.success(
                request,
                f"Attendance for {mark_date.isoformat()} marked as {'Present' if obj.present else 'Absent'}.",
            )
            return redirect('attendance')

        start_date = request.GET.get('start_date') or ''
        end_date = request.GET.get('end_date') or ''

        records = staff.attendance_records.all().order_by('-date')  # pyright: ignore[reportAttributeAccessIssue]
        if start_date:
            try:
                records = records.filter(date__gte=start_date)
            except Exception:
                messages.warning(request, 'Invalid start date filter ignored.')
        if end_date:
            try:
                records = records.filter(date__lte=end_date)
            except Exception:
                messages.warning(request, 'Invalid end date filter ignored.')

        total = records.count()
        present = records.filter(present=True).count()
        absent = records.filter(present=False).count()
        percent = round((present / total) * 100, 1) if total else 0.0

        context = {
            'records': records,
            'total_days': total,
            'days_present': present,
            'days_absent': absent,
            'attendance_percent': percent,
            'start_date': start_date,
            'end_date': end_date,
            'today': timezone.now().date(),
        }
        return render(request, 'core/attendance_staff.html', context)

    # If reached here, user doesn't match student/staff and isn't plain admin
    messages.error(request, "You don't have an attendance view. Contact admin if this is unexpected.")
    return redirect('dashboard')


@login_required
@admin_required
def manage_student_attendance(request):
    """Admin tool to search/select students and mark attendance for a selected date."""
    query = request.GET.get('q', '').strip()
    date_str = request.GET.get('date') or ''
    try:
        selected_date = (
            datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else timezone.now().date()
        )
    except Exception:
        selected_date = timezone.now().date()

    students = StudentProfile.objects.select_related('user').all()
    if query:
        students = students.filter(
            Q(user__first_name__icontains=query)
            | Q(user__last_name__icontains=query)
            | Q(admission_number__icontains=query)
        )
    students = students.order_by('user__last_name', 'user__first_name')[:200]

    if request.method == 'POST':
        action = request.POST.get('action')  # 'present' or 'absent'
        ids = request.POST.getlist('student_ids')
        date_post = request.POST.get('date')
        try:
            mark_date = (
                datetime.strptime(date_post, '%Y-%m-%d').date() if date_post else selected_date
            )
        except Exception:
            mark_date = selected_date

        count = 0
        for sid in ids:
            try:
                sp = StudentProfile.objects.get(id=sid)
                rec, _ = StudentAttendance.objects.get_or_create(
                    student=sp,
                    date=mark_date,
                    defaults={'present': True},
                )
                if action == 'present':
                    rec.present = True
                elif action == 'absent':
                    rec.present = False
                rec.save()
                count += 1
            except StudentProfile.DoesNotExist:
                continue
        if count:
            status = 'present' if action == 'present' else 'absent'
            messages.success(
                request,
                f"Marked {count} student(s) as {status} for {mark_date}.",
            )
        else:
            messages.info(request, 'No students selected.')
        # Redirect with current filters
        return redirect(f"{request.path}?q={query}&date={mark_date.isoformat()}")

    context = {
        'students': students,
        'q': query,
        'selected_date': selected_date,
    }
    return render(request, 'core/attendance_manage_students.html', context)


@login_required
@role_required(['admin', 'it_support'])
def manage_staff_attendance(request):
    """Admin/IT tool to search/select staff and mark attendance for a selected date."""
    query = request.GET.get('q', '').strip()
    date_str = request.GET.get('date') or ''
    try:
        selected_date = (
            datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else timezone.now().date()
        )
    except Exception:
        selected_date = timezone.now().date()

    staff_qs = StaffProfile.objects.select_related('user').all()
    if query:
        staff_qs = staff_qs.filter(
            Q(user__first_name__icontains=query)
            | Q(user__last_name__icontains=query)
            | Q(staff_id__icontains=query)
            | Q(department__icontains=query)
        )
    staff_qs = staff_qs.order_by('user__last_name', 'user__first_name')[:200]

    if request.method == 'POST':
        action = request.POST.get('action')  # 'present' or 'absent'
        ids = request.POST.getlist('staff_ids')
        date_post = request.POST.get('date')
        try:
            mark_date = (
                datetime.strptime(date_post, '%Y-%m-%d').date() if date_post else selected_date
            )
        except Exception:
            mark_date = selected_date

        count = 0
        for sid in ids:
            try:
                sp = StaffProfile.objects.get(id=sid)
                rec, _ = StaffAttendance.objects.get_or_create(
                    staff=sp,
                    date=mark_date,
                    defaults={'present': True, 'created_by': request.user},
                )
                if action == 'present':
                    rec.present = True
                elif action == 'absent':
                    rec.present = False
                if rec.created_by is None:
                    rec.created_by = request.user
                rec.save()
                count += 1
            except StaffProfile.DoesNotExist:
                continue
        if count:
            status = 'present' if action == 'present' else 'absent'
            messages.success(
                request,
                f"Marked {count} staff as {status} for {mark_date}.",
            )
        else:
            messages.info(request, 'No staff selected.')
        # Redirect with current filters
        return redirect(f"{request.path}?q={query}&date={mark_date.isoformat()}")

    context = {
        'staff_list': staff_qs,
        'q': query,
        'selected_date': selected_date,
    }
    return render(request, 'core/attendance_manage_staff.html', context)
