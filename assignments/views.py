from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from core.decorators import role_required
from .models import Assignment, Submission
from .forms import AssignmentForm, SubmissionForm, SubmissionGradeForm

 
@login_required
def assignments_home(request):
    return render(request, 'assignments/assignments_home.html')

 
@login_required
@role_required(['student'])
def student_assignments(request):
    # Show assignments and allow submission upload
    assignments = Assignment.objects.all().order_by('-due_date')
    submissions = Submission.objects.filter(student__user=request.user)
    context = {
        'assignments': assignments,
        'submissions': submissions,
    }
    return render(request, 'assignments/student_assignments.html', context)

 
@login_required
@role_required(['staff', 'admin'])
def staff_assignments(request):
    # List and create assignments
    if request.method == 'POST':
        form = AssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.created_by = request.user
            assignment.save()
            messages.success(request, 'Assignment created.')
            return redirect('assignments:staff_assignments')
    else:
        form = AssignmentForm()

    assignments = Assignment.objects.all().order_by('-created_at')
    context = {
        'form': form,
        'assignments': assignments,
    }
    return render(request, 'assignments/staff_assignments.html', context)


@login_required
@role_required(['student'])
def submit_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            from students.models import StudentProfile
            # Gracefully handle users without a student profile (e.g., superusers)
            student_profile = StudentProfile.objects.filter(user=request.user).first()
            if not student_profile:
                messages.error(request, 'You need a student profile to submit assignments.')
                return redirect('assignments:student_assignments')
            submission.student = student_profile
            submission.assignment = assignment
            submission.save()
            messages.success(request, 'Submission uploaded.')
            return redirect('assignments:student_assignments')
    else:
        form = SubmissionForm()
    return render(request, 'assignments/submit.html', {'assignment': assignment, 'form': form})


@login_required
@role_required(['staff', 'admin'])
def grade_submission(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id)
    if request.method == 'POST':
        form = SubmissionGradeForm(request.POST, instance=submission)
        if form.is_valid():
            graded = form.save(commit=False)
            graded.graded_by = request.user
            graded.graded_at = timezone.now()
            graded.save()
            messages.success(request, 'Submission graded.')
            return redirect('assignments:staff_assignments')
    else:
        form = SubmissionGradeForm(instance=submission)
    return render(request, 'assignments/grade.html', {'submission': submission, 'form': form})
