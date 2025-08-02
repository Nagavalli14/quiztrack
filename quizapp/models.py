from django.db import models
from django.contrib.auth.models import User  # Used in StudentAnswer and Result
'''
# Custom teacher model mapped to raw SQL table
class teacher(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.TextField()
    password = models.TextField()

    class Meta:
        db_table = 'teacher'
        managed = False  # Don't let Django manage this table

# Custom student model mapped to raw SQL table
class student(models.Model):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)

    class Meta:
        db_table = 'student'
        managed = False  # Don't let Django manage this table

# Test model linked to teacher
class Test(models.Model):
    name = models.CharField(max_length=200)
    date = models.DateField()
    uploaded_by = models.ForeignKey('teacher', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

# Quiz model (actual question bank)
class Quiz(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    question = models.TextField()
    option_a = models.CharField(max_length=200)
    option_b = models.CharField(max_length=200)
    option_c = models.CharField(max_length=200)
    option_d = models.CharField(max_length=200)
    correct_option = models.CharField(max_length=1)  # A/B/C/D
    answer = models.CharField(max_length=200)  # for subjective or detailed answer (if needed)

    def __str__(self):
        return self.question[:50]  # Show first 50 chars

# StudentAnswer model - tracks quiz attempts
class StudentAnswer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    selected_option = models.CharField(max_length=1)  # A/B/C/D
    submitted_at = models.DateTimeField(auto_now_add=True)

# Result model - final score and status
class Result(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    answered = models.IntegerField()
    auto_score = models.IntegerField()
    final_score = models.IntegerField(null=True, blank=True)  # Manual eval override
    attempt_time = models.DateTimeField(auto_now_add=True)
    evaluated = models.BooleanField(default=False)  # Whether teacher has finalized result
'''
from django.db import models
from django.contrib.auth.models import User  # Used in StudentAnswer and Result

# Custom teacher model mapped to raw SQL table
class teacher(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.TextField()
    password = models.TextField()

    class Meta:
        db_table = 'teacher'
        managed = False  # Don't let Django manage this table

# Custom student model mapped to raw SQL table
class student(models.Model):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)

    class Meta:
        db_table = 'student'
        managed = False  # Don't let Django manage this table

# Test model linked to teacher
class Test(models.Model):
    name = models.CharField(max_length=200)
    date = models.DateField()
    uploaded_by = models.ForeignKey('teacher', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

# Quiz model (actual question bank)
class Quiz(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    question = models.TextField()
    option_a = models.CharField(max_length=200)
    option_b = models.CharField(max_length=200)
    option_c = models.CharField(max_length=200)
    option_d = models.CharField(max_length=200)
    correct_option = models.CharField(max_length=1)  # A/B/C/D
    answer = models.CharField(max_length=200)  # for subjective or detailed answer (if needed)

    def __str__(self):
        return self.question[:50]  # Show first 50 chars

# StudentAnswer model - tracks quiz attempts
class StudentAnswer(models.Model):
    user = models.ForeignKey(student, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    selected_option = models.CharField(max_length=1)  # A/B/C/D
    submitted_at = models.DateTimeField(auto_now_add=True)

# Result model - final score and status
class Result(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    answered = models.IntegerField()
    auto_score = models.IntegerField()
    final_score = models.IntegerField(null=True, blank=True)  # Manual eval override
    attempt_time = models.DateTimeField(auto_now_add=True)
    evaluated = models.BooleanField(default=False)  # Whether teacher has finalized result