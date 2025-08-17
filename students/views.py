from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib import messages
 
from django.utils import timezone
from core.decorators import role_required
from students.models import StudentProfile
from results.models import StudentResult, TermResult, AcademicSession, AcademicTerm, Subject
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from io import BytesIO


@login_required
@role_required(['student'])
def student_home(request):
    return render(request, 'students/student_home.html')


@login_required
@role_required(['student'])
def assignments(request):
    # Redirect to canonical assignments module
    return HttpResponseRedirect(reverse('assignments:student_assignments'))


@login_required
@role_required(['student'])
def results(request):
    """Display student's results with filters"""
    try:
        student_profile = StudentProfile.objects.get(user=request.user)
        
        # Get filter parameters
        session_id = request.GET.get('session')
        term_id = request.GET.get('term')
        subject_id = request.GET.get('subject')
        
        # Base queryset
        results_queryset = StudentResult.objects.filter(
            student=student_profile
        ).select_related(
            'subject', 'assessment', 'session', 'term', 'student_class'
        ).order_by('-session__start_date', '-term__name', 'subject__name', 'assessment__name')
        
        # Apply filters
        if session_id:
            results_queryset = results_queryset.filter(session_id=session_id)
        if term_id:
            results_queryset = results_queryset.filter(term_id=term_id)
        if subject_id:
            results_queryset = results_queryset.filter(subject_id=subject_id)
        
        # Get compiled term results
        term_results = TermResult.objects.filter(
            student=student_profile
        ).select_related(
            'subject', 'session', 'term', 'student_class'
        ).order_by('-session__start_date', '-term__name', 'subject__name')
        
        # Apply same filters to term results
        if session_id:
            term_results = term_results.filter(session_id=session_id)
        if term_id:
            term_results = term_results.filter(term_id=term_id)
        if subject_id:
            term_results = term_results.filter(subject_id=subject_id)
        
        # Get filter options
        sessions = AcademicSession.objects.all().order_by('-start_date')
        terms = AcademicTerm.objects.all().order_by('session__start_date', 'name')
        subjects = Subject.objects.filter(
            is_active=True,
            studentresult__student=student_profile
        ).distinct().order_by('name')
        
        # Calculate statistics
        total_results = results_queryset.count()
        avg_percentage = 0
        if total_results > 0:
            total_score = sum(result.score for result in results_queryset)
            total_possible = sum(result.assessment.max_score for result in results_queryset)
            avg_percentage = (total_score / total_possible * 100) if total_possible > 0 else 0
        
        context = {
            'student_profile': student_profile,
            'results': results_queryset,
            'term_results': term_results,
            'sessions': sessions,
            'terms': terms,
            'subjects': subjects,
            'selected_session': session_id,
            'selected_term': term_id,
            'selected_subject': subject_id,
            'total_results': total_results,
            'avg_percentage': round(avg_percentage, 2),
        }
        
    except StudentProfile.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        context = {
            'results': [],
            'term_results': [],
            'sessions': [],
            'terms': [],
            'subjects': [],
        }
    
    return render(request, 'students/results.html', context)


@login_required
def attendance(request):
    # Canonical attendance is handled in core. If user isn't a student, redirect there.
    user = request.user
    if not hasattr(user, 'student_profile'):
        return HttpResponseRedirect(reverse('attendance'))

    # Show logged-in student's attendance with optional date filters
    try:
        student_profile = StudentProfile.objects.get(user=user)

        # Optional filters: start_date and end_date in YYYY-MM-DD
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        records = (
            student_profile.attendance_records.all().order_by('-date')  # pyright: ignore[reportAttributeAccessIssue]
        )
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
            'student_profile': student_profile,
            'records': records,
            'total_days': total,
            'days_present': present,
            'days_absent': absent,
            'attendance_percent': percent,
            'start_date': start_date or '',
            'end_date': end_date or '',
        }
    except StudentProfile.DoesNotExist:
        # If no profile, use core attendance (admin/staff)
        return HttpResponseRedirect(reverse('attendance'))

    return render(request, 'students/attendance.html', context)


@login_required
@role_required(['student'])
def result_sheets(request):
    """Display student's result sheets for printing"""
    try:
        student_profile = StudentProfile.objects.get(user=request.user)
        
        # Get filter parameters
        session_id = request.GET.get('session')
        term_id = request.GET.get('term')
        
        # Get available sessions and terms for this student
        available_sessions = AcademicSession.objects.filter(
            termresult__student=student_profile
        ).distinct().order_by('-start_date')
        
        available_terms = AcademicTerm.objects.filter(
            termresult__student=student_profile
        ).distinct().order_by('session__start_date', 'name')
        
        result_sheets = []
        
        if session_id and term_id:
            # Get term results for the selected session and term
            term_results = TermResult.objects.filter(
                student=student_profile,
                session_id=session_id,
                term_id=term_id
            ).select_related(
                'subject', 'session', 'term', 'student_class'
            ).order_by('subject__name')
            
            if term_results.exists():
                # Calculate overall statistics
                total_score = sum(tr.total_score for tr in term_results)
                total_possible = sum(tr.total_possible for tr in term_results)
                overall_percentage = (total_score / total_possible * 100) if total_possible > 0 else 0
                
                # Calculate overall grade
                if overall_percentage >= 80:
                    overall_grade = 'A'
                elif overall_percentage >= 70:
                    overall_grade = 'B'
                elif overall_percentage >= 60:
                    overall_grade = 'C'
                elif overall_percentage >= 50:
                    overall_grade = 'D'
                else:
                    overall_grade = 'F'

                first_tr = term_results.first()
                if first_tr is not None:
                    result_sheets.append({
                        'session': first_tr.session,
                        'term': first_tr.term,
                        'student_class': first_tr.student_class,
                        'term_results': term_results,
                        'total_score': total_score,
                        'total_possible': total_possible,
                        'overall_percentage': round(overall_percentage, 2),
                        'overall_grade': overall_grade,
                        'subject_count': term_results.count(),
                    })
        
        context = {
            'student_profile': student_profile,
            'available_sessions': available_sessions,
            'available_terms': available_terms,
            'selected_session': session_id,
            'selected_term': term_id,
            'result_sheets': result_sheets,
        }
        
    except StudentProfile.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        context = {
            'available_sessions': [],
            'available_terms': [],
            'result_sheets': [],
        }
    
    return render(request, 'students/result_sheets.html', context)


@login_required
@role_required(['student'])
def print_result_sheet(request, session_id, term_id):
    """Generate and download PDF result sheet"""
    try:
        student_profile = StudentProfile.objects.get(user=request.user)
        session = get_object_or_404(AcademicSession, id=session_id)
        term = get_object_or_404(AcademicTerm, id=term_id)

        # Get term results
        term_results = TermResult.objects.filter(
            student=student_profile,
            session=session,
            term=term
        ).select_related('subject', 'student_class').order_by('subject__name')

        if not term_results.exists():
            messages.error(request, 'No results found for the selected session and term.')
            return HttpResponseRedirect(reverse('students:result_sheets'))

        # Create PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)

        # Build content
        content = []
        styles = getSampleStyleSheet()

        # School header
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1  # Center
        )

        content.append(Paragraph("GLAD TIDINGS SCHOOL", title_style))
        content.append(Paragraph("STUDENT RESULT SHEET", styles['Heading2']))
        content.append(Spacer(1, 20))

        # Student info
        first_tr = term_results.first()
        term_label = dict(AcademicTerm.TERM_CHOICES).get(term.name, term.name)
        student_info = [
            ['Student Name:', student_profile.user.get_full_name()],
            ['Admission Number:', student_profile.admission_number or 'N/A'],
            ['Class:', first_tr.student_class.name if first_tr else 'N/A'],
            ['Session:', session.name],
            ['Term:', term_label],
        ]

        info_table = Table(student_info, colWidths=[2*inch, 3*inch])
        info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))

        content.append(info_table)
        content.append(Spacer(1, 30))

        # Results table
        data = [['Subject', 'Score', 'Grade', 'Remarks']]

        total_score = 0
        total_possible = 0

        for result in term_results:
            data.append([
                result.subject.name,
                f"{result.total_score}/{result.total_possible}",
                result.grade,
                result.teacher_remarks or '-'
            ])
            total_score += result.total_score
            total_possible += result.total_possible

        # Add totals
        overall_percentage = (total_score / total_possible * 100) if total_possible > 0 else 0
        if overall_percentage >= 80:
            overall_grade = 'A'
        elif overall_percentage >= 70:
            overall_grade = 'B'
        elif overall_percentage >= 60:
            overall_grade = 'C'
        elif overall_percentage >= 50:
            overall_grade = 'D'
        else:
            overall_grade = 'F'

        data.append(['', '', '', ''])  # Empty row
        data.append(['TOTAL', f"{total_score}/{total_possible}", overall_grade, f"{overall_percentage:.1f}%"])

        results_table = Table(data, colWidths=[2.5*inch, 1.5*inch, 1*inch, 2*inch])
        results_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -3), colors.beige),
            ('BACKGROUND', (0, -2), (-1, -1), colors.lightgrey),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        content.append(results_table)
        content.append(Spacer(1, 50))

        # Footer
        footer_text = f"Generated on: {timezone.now().strftime('%B %d, %Y')}"
        content.append(Paragraph(footer_text, styles['Normal']))

        # Build PDF
        doc.build(content)

        # Return response
        buffer.seek(0)
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        filename = f"{student_profile.user.get_full_name()}_{session.name}_{term_label}_results.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        return response
    except StudentProfile.DoesNotExist:
        messages.error(request, 'Student profile not found.')
        return HttpResponseRedirect(reverse('students:result_sheets'))
    except Exception as e:
        messages.error(request, f'Error generating result sheet: {str(e)}')
        return HttpResponseRedirect(reverse('students:result_sheets'))
