from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q, Avg, Count, Max
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.template.loader import render_to_string
import json
import csv
from io import StringIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

from core.decorators import role_required
from students.models import StudentProfile
from staff.models import StaffProfile
from results.models import (
    AcademicSession, AcademicTerm, Subject, StudentClass, Assessment,
    StudentResult, TermResult, ResultSheet
)


@login_required
@role_required(['staff', 'admin'])
def result_dashboard(request):
    """Dashboard for result management"""
    current_session = AcademicSession.objects.filter(is_current=True).first()
    current_term = AcademicTerm.objects.filter(is_current=True).first()
    
    # Get statistics
    stats = {
        'total_students': StudentProfile.objects.count(),
        'total_subjects': Subject.objects.filter(is_active=True).count(),
        'total_classes': StudentClass.objects.filter(is_active=True).count(),
        'results_entered': StudentResult.objects.count(),
    }
    
    if current_session and current_term:
        stats['current_term_results'] = StudentResult.objects.filter(
            session=current_session,
            term=current_term
        ).count()
    
    # Recent activities
    recent_results = StudentResult.objects.select_related(
        'student__user', 'subject', 'assessment'
    ).order_by('-entered_at')[:10]
    
    context = {
        'current_session': current_session,
        'current_term': current_term,
        'stats': stats,
        'recent_results': recent_results,
    }
    
    return render(request, 'results/dashboard.html', context)


@login_required
@role_required(['staff', 'admin'])
def result_entry(request):
    """Form for entering student results"""
    if request.method == 'POST':
        return handle_result_entry(request)
    
    # Get form data
    sessions = AcademicSession.objects.all()
    terms = AcademicTerm.objects.all()
    subjects = Subject.objects.filter(is_active=True)
    classes = StudentClass.objects.filter(is_active=True)
    assessments = Assessment.objects.filter(is_active=True)
    
    context = {
        'sessions': sessions,
        'terms': terms,
        'subjects': subjects,
        'classes': classes,
        'assessments': assessments,
    }
    
    return render(request, 'results/result_entry.html', context)


def handle_result_entry(request):
    """Handle result entry form submission"""
    try:
        with transaction.atomic():
            session_id = request.POST.get('session')
            term_id = request.POST.get('term')
            subject_id = request.POST.get('subject')
            class_id = request.POST.get('student_class')
            assessment_id = request.POST.get('assessment')
            student_id = request.POST.get('student')
            score = request.POST.get('score')
            remarks = request.POST.get('remarks', '')
            
            # Get objects
            session = get_object_or_404(AcademicSession, id=session_id)
            term = get_object_or_404(AcademicTerm, id=term_id)
            subject = get_object_or_404(Subject, id=subject_id)
            student_class = get_object_or_404(StudentClass, id=class_id)
            assessment = get_object_or_404(Assessment, id=assessment_id)
            student = get_object_or_404(StudentProfile, id=student_id)
            
            # Validate score
            if not score or not score.strip():
                messages.error(request, 'Score is required.')
                return redirect('results:result_entry')
                
            try:
                score_value = float(score)
                if score_value < 0 or score_value > assessment.max_score:
                    messages.error(request, f'Score must be between 0 and {assessment.max_score}.')
                    return redirect('results:result_entry')
            except ValueError:
                messages.error(request, 'Invalid score format.')
                return redirect('results:result_entry')
            
            # Get or create result
            result, created = StudentResult.objects.get_or_create(
                student=student,
                subject=subject,
                session=session,
                term=term,
                student_class=student_class,
                assessment=assessment,
                defaults={
                    'score': score_value,
                    'remarks': remarks,
                    'entered_by': request.user
                }
            )
            
            if not created:
                result.score = score_value
                result.remarks = remarks
                result.entered_by = request.user
                result.save()
                messages.success(request, 'Result updated successfully!')
            else:
                messages.success(request, 'Result saved successfully!')
                
    except Exception as e:
        messages.error(request, f'Error saving result: {str(e)}')
    
    return redirect('results:result_entry')


@login_required
@role_required(['staff', 'admin'])
def get_class_students(request):
    """AJAX endpoint to get students in a class"""
    class_id = request.GET.get('class_id')
    
    if not class_id:
        return JsonResponse({'error': 'Class ID is required'}, status=400)
    
    try:
        student_class = get_object_or_404(StudentClass, id=class_id)
        
        # Get students in the class - for now, we'll get all active students
        # You may need to add a proper class assignment system later
        students = StudentProfile.objects.filter(
            user__is_active=True
        ).select_related('user').order_by('user__last_name', 'user__first_name')
        
        students_data = []
        for student in students:
            students_data.append({
                'id': student.id,
                'name': student.user.get_full_name(),
                'admission_number': student.admission_number or 'N/A'
            })
        
        return JsonResponse({
            'students': students_data,
            'class_name': student_class.name
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@role_required(['staff', 'admin'])
def compile_results(request):
    """Compile term results from individual assessments"""
    if request.method == 'POST':
        session_id = request.POST.get('session')
        term_id = request.POST.get('term')
        class_id = request.POST.get('student_class')
        
        try:
            with transaction.atomic():
                session = get_object_or_404(AcademicSession, id=session_id)
                term = get_object_or_404(AcademicTerm, id=term_id)
                student_class = get_object_or_404(StudentClass, id=class_id)
                
                # Get all students in the class
                students = StudentProfile.objects.filter(user__is_active=True)
                
                compiled_count = 0
                for student in students:
                    # Get all subjects for this class
                    for subject in student_class.subjects.all():
                        # Create or get term result
                        term_result, created = TermResult.objects.get_or_create(
                            student=student,
                            subject=subject,
                            session=session,
                            term=term,
                            student_class=student_class,
                            defaults={'compiled_by': request.user}
                        )
                        
                        # Compile the result
                        term_result.compile_result()
                        if not created:
                            term_result.compiled_by = request.user
                            term_result.save()
                        
                        compiled_count += 1
                
                # Calculate positions
                calculate_positions(session, term, student_class)
                
                messages.success(
                    request,
                    f'Results compiled successfully! {compiled_count} term results processed.'
                )
                
        except Exception as e:
            messages.error(request, f'Error compiling results: {str(e)}')
    
    # Get form data
    sessions = AcademicSession.objects.all()
    terms = AcademicTerm.objects.all()
    classes = StudentClass.objects.filter(is_active=True)
    
    context = {
        'sessions': sessions,
        'terms': terms,
        'classes': classes,
    }
    
    return render(request, 'results/compile.html', context)


def calculate_positions(session, term, student_class):
    """Calculate student positions in class"""
    # Calculate positions for each subject
    subjects = student_class.subjects.all()
    
    for subject in subjects:
        term_results = TermResult.objects.filter(
            session=session,
            term=term,
            student_class=student_class,
            subject=subject
        ).order_by('-percentage')
        
        total_students = term_results.count()
        
        for position, result in enumerate(term_results, 1):
            result.position_in_class = position
            result.total_students = total_students
            result.save()


@login_required
@role_required(['staff', 'admin'])
def result_sheets(request):
    """Manage result sheets"""
    if request.method == 'POST':
        return generate_result_sheets(request)
    
    # Get published result sheets
    result_sheets = ResultSheet.objects.select_related(
        'student__user', 'session', 'term', 'student_class'
    ).order_by('-session', '-term', 'student__user__last_name')
    
    # Pagination
    paginator = Paginator(result_sheets, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get form data
    sessions = AcademicSession.objects.all()
    terms = AcademicTerm.objects.all()
    classes = StudentClass.objects.filter(is_active=True)
    
    context = {
        'page_obj': page_obj,
        'sessions': sessions,
        'terms': terms,
        'classes': classes,
    }
    
    return render(request, 'results/sheets.html', context)


def generate_result_sheets(request):
    """Generate result sheets for students"""
    try:
        with transaction.atomic():
            session_id = request.POST.get('session')
            term_id = request.POST.get('term')
            class_id = request.POST.get('student_class')
            
            session = get_object_or_404(AcademicSession, id=session_id)
            term = get_object_or_404(AcademicTerm, id=term_id)
            student_class = get_object_or_404(StudentClass, id=class_id)
            
            # Get students in the class
            students = StudentProfile.objects.filter(user__is_active=True)
            
            sheets_generated = 0
            for student in students:
                # Create or get result sheet
                result_sheet, created = ResultSheet.objects.get_or_create(
                    student=student,
                    session=session,
                    term=term,
                    student_class=student_class
                )
                
                # Compile the result sheet
                result_sheet.compile_result_sheet()
                sheets_generated += 1
            
            messages.success(
                request, 
                f'{sheets_generated} result sheets generated successfully!'
            )
            
    except Exception as e:
        messages.error(request, f'Error generating result sheets: {str(e)}')
    
    return redirect('academics:result_sheets')


@login_required
@role_required(['staff', 'admin'])
def print_result_sheet(request, sheet_id):
    """Generate printable PDF result sheet"""
    result_sheet = get_object_or_404(ResultSheet, id=sheet_id)
    
    # Get term results for this student
    term_results = TermResult.objects.filter(
        student=result_sheet.student,
        session=result_sheet.session,
        term=result_sheet.term
    ).select_related('subject').order_by('subject__name')
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="result_sheet_{result_sheet.student.admission_number}_{result_sheet.session.name}_{result_sheet.term.name}.pdf"'
    
    # Create PDF
    doc = SimpleDocTemplate(response, pagesize=A4)
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1,  # Center alignment
    )
    
    story.append(Paragraph("GLAD TIDINGS SCHOOL", title_style))
    story.append(Paragraph("STUDENT RESULT SHEET", title_style))
    story.append(Spacer(1, 20))
    
    # Student details
    student_info = [
        ['Student Name:', result_sheet.student.user.get_full_name()],
        ['Admission Number:', result_sheet.student.admission_number],
        ['Class:', result_sheet.student_class.name],
        ['Session:', result_sheet.session.name],
        ['Term:', result_sheet.term.get_name_display()],
    ]
    
    student_table = Table(student_info, colWidths=[2*inch, 4*inch])
    student_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (1, 0), (1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(student_table)
    story.append(Spacer(1, 20))
    
    # Results table
    results_data = [['Subject', 'Score', 'Grade', 'Position', 'Remarks']]
    
    for result in term_results:
        results_data.append([
            result.subject.name,
            f"{result.percentage:.1f}%",
            result.grade,
            f"{result.position_in_class}/{result.total_students}" if result.position_in_class else "N/A",
            result.teacher_remarks[:50] if result.teacher_remarks else ""
        ])
    
    results_table = Table(results_data, colWidths=[2*inch, 1*inch, 0.8*inch, 1*inch, 2*inch])
    results_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(results_table)
    story.append(Spacer(1, 20))
    
    # Overall performance
    overall_info = [
        ['Overall Percentage:', f"{result_sheet.overall_percentage:.1f}%"],
        ['Overall Grade:', result_sheet.overall_grade],
        ['Position in Class:', f"{result_sheet.position_in_class}/{result_sheet.total_students}" if result_sheet.position_in_class else "N/A"],
    ]
    
    overall_table = Table(overall_info, colWidths=[2*inch, 2*inch])
    overall_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(overall_table)
    story.append(Spacer(1, 20))
    
    # Comments
    if result_sheet.class_teacher_remarks:
        story.append(Paragraph("<b>Class Teacher's Remarks:</b>", styles['Heading3']))
        story.append(Paragraph(result_sheet.class_teacher_remarks, styles['Normal']))
        story.append(Spacer(1, 10))
    
    if result_sheet.principal_remarks:
        story.append(Paragraph("<b>Principal's Remarks:</b>", styles['Heading3']))
        story.append(Paragraph(result_sheet.principal_remarks, styles['Normal']))
    
    doc.build(story)
    return response


@login_required
@role_required(['staff', 'admin'])
def bulk_upload_results(request):
    """Bulk upload results via CSV"""
    if request.method == 'POST':
        return handle_bulk_upload(request)
    
    # Get form data
    sessions = AcademicSession.objects.all()
    terms = AcademicTerm.objects.all()
    subjects = Subject.objects.filter(is_active=True)
    classes = StudentClass.objects.filter(is_active=True)
    assessments = Assessment.objects.filter(is_active=True)
    
    context = {
        'sessions': sessions,
        'terms': terms,
        'subjects': subjects,
        'classes': classes,
        'assessments': assessments,
    }
    
    return render(request, 'results/bulk_upload.html', context)


def handle_bulk_upload(request):
    """Handle CSV bulk upload"""
    try:
        csv_file = request.FILES.get('csv_file')
        if not csv_file:
            messages.error(request, 'Please select a CSV file.')
            return redirect('academics:bulk_upload_results')
        
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'Please upload a valid CSV file.')
            return redirect('academics:bulk_upload_results')
        
        # Get form parameters
        session = get_object_or_404(AcademicSession, id=request.POST.get('session'))
        term = get_object_or_404(AcademicTerm, id=request.POST.get('term'))
        subject = get_object_or_404(Subject, id=request.POST.get('subject'))
        student_class = get_object_or_404(StudentClass, id=request.POST.get('student_class'))
        assessment = get_object_or_404(Assessment, id=request.POST.get('assessment'))
        
        # Read CSV file
        decoded_file = csv_file.read().decode('utf-8')
        csv_data = StringIO(decoded_file)
        reader = csv.DictReader(csv_data)
        
        created_count = 0
        updated_count = 0
        error_count = 0
        errors = []
        
        with transaction.atomic():
            for row_num, row in enumerate(reader, start=2):  # Start from 2 because of header
                try:
                    admission_number = row.get('admission_number', '').strip()
                    score = row.get('score', '').strip()
                    
                    if not admission_number or not score:
                        continue
                    
                    # Get student
                    try:
                        student = StudentProfile.objects.get(admission_number=admission_number)
                    except StudentProfile.DoesNotExist:
                        errors.append(f"Row {row_num}: Student with admission number '{admission_number}' not found.")
                        error_count += 1
                        continue
                    
                    # Validate score
                    try:
                        score = float(score)
                        if score < 0 or score > assessment.max_score:
                            errors.append(f"Row {row_num}: Invalid score '{score}' for {admission_number}. Must be between 0 and {assessment.max_score}.")
                            error_count += 1
                            continue
                    except ValueError:
                        errors.append(f"Row {row_num}: Invalid score format '{score}' for {admission_number}.")
                        error_count += 1
                        continue
                    
                    # Create or update result
                    result, created = StudentResult.objects.get_or_create(
                        student=student,
                        subject=subject,
                        session=session,
                        term=term,
                        student_class=student_class,
                        assessment=assessment,
                        defaults={
                            'score': score,
                            'entered_by': request.user
                        }
                    )
                    
                    if created:
                        created_count += 1
                    else:
                        result.score = score
                        result.entered_by = request.user
                        result.save()
                        updated_count += 1
                        
                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)}")
                    error_count += 1
        
        # Show results
        if created_count > 0 or updated_count > 0:
            messages.success(
                request, 
                f'Upload completed! {created_count} new results created, {updated_count} results updated.'
            )
        
        if error_count > 0:
            messages.warning(
                request, 
                f'{error_count} errors occurred during upload. Check the details below.'
            )
            for error in errors[:10]:  # Show first 10 errors
                messages.error(request, error)
            
            if len(errors) > 10:
                messages.info(request, f'... and {len(errors) - 10} more errors.')
        
    except Exception as e:
        messages.error(request, f'Upload failed: {str(e)}')
    
    return redirect('academics:bulk_upload_results')


@login_required
def download_csv_template(request):
    """Download CSV template for bulk upload"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="results_upload_template.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['admission_number', 'score', 'remarks'])
    writer.writerow(['ST2024001', '85', 'Good performance'])
    writer.writerow(['ST2024002', '92', 'Excellent work'])
    writer.writerow(['ST2024003', '78', 'Needs improvement'])
    
    return response
