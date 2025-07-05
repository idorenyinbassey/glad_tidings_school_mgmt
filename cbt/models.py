from django.conf import settings
from django.db import models
from django.utils import timezone


class CBTExam(models.Model):
    title = models.CharField(max_length=200)
    subject = models.CharField(max_length=100)
    assigned_class = models.CharField(max_length=50)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    total_marks = models.PositiveIntegerField(default=100)
    pass_mark = models.PositiveIntegerField(default=50)
    instructions = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='cbt_created'
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.subject} ({self.assigned_class})"


class CBTQuestion(models.Model):
    exam = models.ForeignKey(CBTExam, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    option_a = models.CharField(max_length=500)
    option_b = models.CharField(max_length=500)
    option_c = models.CharField(max_length=500)
    option_d = models.CharField(max_length=500)
    correct_option = models.CharField(
        max_length=1, 
        choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')]
    )
    marks = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.exam.title} - {self.question_text[:50]}..."


class CBTSession(models.Model):
    exam = models.ForeignKey(CBTExam, on_delete=models.CASCADE, related_name='sessions')
    student = models.ForeignKey(
        'students.StudentProfile', 
        on_delete=models.CASCADE, 
        related_name='cbt_sessions'
    )
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    is_submitted = models.BooleanField(default=False)

    class Meta:
        unique_together = ['exam', 'student']
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.exam.title}"

    def calculate_score(self):
        """Calculate the score based on correct answers"""
        if not self.is_submitted:
            return None

        correct_answers = self.answers.filter(is_correct=True)
        total_marks = sum(answer.question.marks for answer in correct_answers)
        total_possible = sum(q.marks for q in self.exam.questions.all())

        if total_possible > 0:
            self.score = total_marks
            self.percentage = (self.score / total_possible) * 100
        else:
            self.score = 0
            self.percentage = 0

        self.save(update_fields=['score', 'percentage'])
        return self.score

    def submit_exam(self):
        """Submit the exam and calculate final score"""
        self.completed_at = timezone.now()
        self.is_submitted = True
        self.save()

        # Calculate score
        self.calculate_score()
        return self.score

    @property
    def is_passed(self):
        """Check if student passed the exam"""
        if self.score is None:
            return False
        return self.score >= self.exam.pass_mark


class CBTAnswer(models.Model):
    session = models.ForeignKey(CBTSession, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(CBTQuestion, on_delete=models.CASCADE)
    selected_option = models.CharField(
        max_length=1, 
        choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')]
    )
    is_correct = models.BooleanField(default=False)
    answered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['session', 'question']
        ordering = ['question']

    def __str__(self):
        return f"{self.session.student.user.get_full_name()} - {self.question.question_text[:30]}..."

    def save(self, *args, **kwargs):
        # Check if answer is correct
        self.is_correct = (self.selected_option == self.question.correct_option)
        super().save(*args, **kwargs)
