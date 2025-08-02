from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import logout
from django.db import connection
from .models import Quiz, Result, StudentAnswer, Test, teacher, student
from django.contrib.auth.decorators import login_required
import csv

def home(request):
    return render(request, 'quizapp/home.html')


# ---------- STUDENT VIEWS ----------

def quiz(request, test_id):
    print("🧪 Quiz View Called with test_id:", test_id)
    test = Test.objects.get(id=test_id)
    quizzes = Quiz.objects.filter(test=test)
    print("📋 Loaded quizzes:", quizzes)
    return render(request, 'quizapp/quiz.html', {'test': test, 'quizzes': quizzes})


def quiz_view(request):
    quizzes = Quiz.objects.all()
    return render(request, 'quizapp/quiz.html', {'quizzes': quizzes})


def result_view(request):
    if 'student_username' not in request.session:
        return redirect('student_login')
    results = Result.objects.filter(student__username=request.session['student_username'])
    return render(request, 'quizapp/result.html', {'results': results})


def student_dashboard(request):
    if 'student_username' not in request.session:
        return redirect('student_login')
    
    tests = Test.objects.all()
    print("🧪 Tests visible to students:", tests)
    return render(request, 'quizapp/student_dashboard.html', {'tests': tests})


def student_result(request):
    if 'student_username' not in request.session:
        return redirect('student_login')
    try:
        result = Result.objects.get(student__username=request.session['student_username'])
    except Result.DoesNotExist:
        result = None
    return render(request, 'quizapp/student_result.html', {'result': result})


# ---------- TEACHER VIEWS ----------

def upload_csv(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        test_name = request.POST.get('test_name')
        test_date = request.POST.get('test_date')

        if not test_name or not test_date:
            messages.error(request, "Test Name and Date are required.")
            return redirect('upload_csv')

        teacher_username = request.session.get('teacher_username')
        if not teacher_username:
            messages.error(request, "You are not logged in as a teacher.")
            return redirect('upload_csv')

        try:
            uploaded_by = teacher.objects.get(username=teacher_username)
        except teacher.DoesNotExist:
            messages.error(request, "Teacher user not found in custom table.")
            return redirect('upload_csv')

        test = Test.objects.create(name=test_name, date=test_date, uploaded_by=uploaded_by)

        file = request.FILES['csv_file'].read().decode('utf-8').splitlines()
        reader = csv.reader(file)
        next(reader)

        for row in reader:
            print("📄 Row:", row)
            if len(row) >= 6:
                Quiz.objects.create(
                    question=row[0],
                    option_a=row[1],
                    option_b=row[2],
                    option_c=row[3],
                    option_d=row[4],
                    correct_option=row[5].strip().upper(),
                    
                    test=test
                )
            else:
                print("⚠️ Skipped row (not enough columns):", row)

        messages.success(request, "CSV and Test uploaded successfully!")
        return redirect('upload_csv')

    tests = Test.objects.all().order_by('-date')
    return render(request, 'quizapp/upload_csv.html', {'tests': tests})


def evaluate_results(request):
    if 'teacher_username' not in request.session:
        return redirect('teacher_login')
    if request.method == 'POST':
        for key, value in request.POST.items():
            if key.startswith('score_'):
                attempt_id = key.split('_')[1]
                try:
                    answer = StudentAnswer.objects.get(id=attempt_id)
                    answer.manual_score = int(value)
                    answer.evaluated = True
                    answer.save()
                except StudentAnswer.DoesNotExist:
                    continue
        messages.success(request, "Scores updated successfully!")
        return redirect('evaluate_results')

    answers = StudentAnswer.objects.select_related('user', 'quiz', 'test').order_by('user__username', 'test__name', 'submitted_at')

    student_data = []
    grouped = {}

    for ans in answers:
        key = (ans.user.id, ans.test.id)
        if key not in grouped:
            grouped[key] = {
                'user': ans.user,
                'test': ans.test,
                'attempt_id': ans.id,
                'attempt_time': ans.timestamp,
                'answered': 0,
                'total': Quiz.objects.filter(test=ans.test).count(),
                'auto_score': 0,
                'final_score': ans.manual_score or 0,
                'evaluated': ans.evaluated
            }
        grouped[key]['answered'] += 1
        if ans.selected_option.upper() == ans.quiz.correct_option.upper():
            grouped[key]['auto_score'] += 1

    for key in grouped:
        student_data.append(grouped[key])

    return render(request, 'quizapp/evaluate_answers.html', {'student_data': student_data})


def student_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM student WHERE username = %s AND password = %s", [username, password])
            row = cursor.fetchone()

        if row:
            request.session['student_username'] = username
            return redirect('student_dashboard')
        else:
            messages.error(request, "Invalid credentials")
    return render(request, 'quizapp/login.html')


def teacher_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM teacher WHERE username = %s AND password = %s", [username, password])
            row = cursor.fetchone()

        if row:
            request.session['teacher_username'] = username
            return redirect('upload_csv')
        else:
            messages.error(request, "Invalid credentials")
    return render(request, 'quizapp/login.html')


def delete_test(request, test_id):
    test = get_object_or_404(Test, id=test_id)
    Quiz.objects.filter(test=test).delete()
    test.delete()
    return redirect('upload_csv')


def logout_view(request):
    logout(request)
    return redirect('home')


def submit_quiz(request):
    if 'student_username' not in request.session:
        return redirect('student_login')

    if request.method == "POST":
        username = request.session.get('student_username')
        test_id = request.POST.get('test_id')
        test = Test.objects.get(id=test_id)
        questions = Quiz.objects.filter(test=test)

        correct_count = 0
        total_answered = 0

        # ✅ Get student from custom student model
        try:
            student_obj = student.objects.get(username=username)
        except student.DoesNotExist:
            messages.error(request, "Student not found.")
            return redirect('student_login')

        for question in questions:
            selected = request.POST.get(f'question_{question.id}')
            if selected:
                total_answered += 1
            is_correct = selected and selected.upper() == question.correct_option.upper()
            if is_correct:
                correct_count += 1

            StudentAnswer.objects.create(
    user=student_obj,      # ✅ use `user`, not `student`
    test=test,
    quiz=question,
    selected_option=selected or ""
)


        Result.objects.create(
            student=student_obj,
            test=test,
            answered=total_answered,
            auto_score=correct_count,
            final_score=None,
            evaluated=False
        )

        return redirect('quiz_submitted')  # ✅ This should now work

    return redirect('student_dashboard')


@login_required
def quiz_submitted(request):
    return render(request, 'quizapp/quiz_submitted.html')
