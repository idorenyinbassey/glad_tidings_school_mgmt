from django.conf import settings
from django.db import models

class CBTExam(models.Model):
    title = models.CharField(max_length=200)
    subject = models.CharField(max_length=100)
    assigned_class = models.CharField(max_length=50)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='cbt_created')

    def __str__(self):
        return self.title

class CBTQuestion(models.Model):
    exam = models.ForeignKey(CBTExam, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    option_a = models.CharField(max_length=200)
    option_b = models.CharField(max_length=200)
    option_c = models.CharField(max_length=200)
    option_d = models.CharField(max_length=200)
    correct_option = models.CharField(max_length=1, choices=[('A','A'),('B','B'),('C','C'),('D','D')])

    def __str__(self):
        return f"{self.exam}: {self.question_text[:30]}..."

class CBTSession(models.Model):
    exam = models.ForeignKey(CBTExam, on_delete=models.CASCADE, related_name='sessions')
    student = models.ForeignKey('students.StudentProfile', on_delete=models.CASCADE, related_name='cbt_sessions')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.student} - {self.exam}"

class CBTAnswer(models.Model):
    session = models.ForeignKey(CBTSession, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(CBTQuestion, on_delete=models.CASCADE)
    selected_option = models.CharField(max_length=1, choices=[('A','A'),('B','B'),('C','C'),('D','D')])
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.session} - {self.question}"
