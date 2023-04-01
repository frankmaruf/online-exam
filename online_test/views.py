from django.shortcuts import render, get_object_or_404,redirect
from django.http import JsonResponse
from online_test.models import Question, Examinee, SelectedAnswer, Subscriber,Subject, Teacher
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.http import JsonResponse
from datetime import datetime
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.db.models import Subquery, OuterRef, CharField
# Create your views here.



def index(request):
    examinee = Examinee.objects.count()
    total_question = Question.objects.count()

    try:
        latest_subject = Subject.objects.last()
        total_subject = Subject.objects.count()
        latest_question = Question.objects.filter(subject_id=latest_subject.pk).count() if latest_subject is not None else Question.objects.count()

    except Subject.DoesNotExist:
        latest_subject = None
        latest_question = None
        total_subject = 0

    context = {
        'examinee': examinee,
        'total_subject': total_subject,
        'total_question': total_question,
        'latest_question': latest_question or 0,
    }
    return render(request, "base/base.html", context)

@login_required
def logout_user(request):
    logout(request)
    messages.success(request, ("You have been logged Out..."))
    return redirect('course_list')

def login_user(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "You have been logged in!")
            if user.is_superuser:
                return redirect('dashboard')
            else:
                return redirect('subjects')
        else:
            messages.error(
                request, "Invalid username or password. Please try again.")
    return render(request, "authenticate/login.html")

def signup(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name').strip()
        last_name = request.POST.get('last_name').strip()
        email = request.POST.get('email').strip()
        username = request.POST.get('username').strip()
        password = request.POST.get('password1')
        confirm_password = request.POST.get('password2')
        who_are_you      = request.POST.get('who_are_you')

        if password != confirm_password:
            messages.warning(request,"Password doesn't match")
            return redirect("login_user")

        check_exist = User.objects.filter(Q(username=username) | Q(email=email))
        if check_exist:
            messages.warning("User already exist!")
            return redirect("signup")

        if who_are_you == "teacher":
            user = User.objects.create_user(username=username, email=email, first_name=first_name, last_name=last_name,password = confirm_password, is_superuser = True)
            user.save()
            Teacher.objects.create(user_id = user.id)
        else:
            user = User.objects.create_user(username=username, email=email, first_name=first_name, last_name=last_name,password = confirm_password)
            user.save()
            Examinee.objects.create(user_id = user.id)
        authenticate(request, user=user)
        login(request, user)
        messages.success(request,"You Successfully Log in")
        return redirect('subjects')
    return render(request, 'authenticate/signup.html')

@login_required
@permission_required('online_test.add_subject')
def dashboard(request):
    top_examinees = Examinee.objects.filter(has_completed_exam=True).order_by('-score')[:10]
    examinee = Examinee.objects.count()
    total_question = Question.objects.count()

    try:
        latest_subject = Subject.objects.last()
        total_subject = Subject.objects.count()
        latest_question = Question.objects.filter(subject_id=latest_subject.pk).count() if latest_subject is not None else Question.objects.count()
    except Subject.DoesNotExist:
        latest_subject = None
        latest_question = None
        total_subject = 0

    context = {
        'top_examinees': top_examinees,
        'examinee': examinee,
        'total_subject': total_subject,
        'total_question': total_question,
        'latest_question': latest_question or 0,
    }
    return render(request,'dashmin\index.html',context)


@login_required
@permission_required('online_test.add_subject')
def exam_results(request):
    examinees = Examinee.objects.filter(has_completed_exam=True).order_by('-score')
    context = {
        'examinees' : examinees
    }
    return render(request,'exam_results.html',context)

@login_required
@permission_required('online_test.add_subject')
def examinee_exam_result(request,pk):

    examinee = get_object_or_404(Examinee,id=pk)
    if not examinee.has_completed_exam:
        messages.warning(request, "The examinee haven't attended the exam.")
        return redirect('exam')

    selected_answers = SelectedAnswer.objects.filter(
            examinee=examinee,
            question=OuterRef('pk'),
        ).order_by('-id')

    questions = Question.objects.all().annotate(
            selected_answer=Subquery(selected_answers.values('selected_mcq_option')[:1], output_field=CharField())
        ).annotate(
            long_answer=Subquery(selected_answers.values('selected_long_answer')[:1], output_field=CharField())
        )

    context = {
        'score': examinee.score,
        "examinee": examinee,
        "questions": questions
        }
    return render(request, 'exam_result.html', context)

@login_required
def logout_user(request):
    logout(request)
    messages.success(request, ("You have been logged Out..."))
    return redirect('index')

@login_required
@permission_required('online_test.add_subject')
def add_new_subject(request):
    if request.method == "POST":
        name          = request.POST.get('name').strip()

        check_exist = Subject.objects.filter(name__icontains=name).exists()
        if check_exist:
            messages.warning(request,"Subject Already exist!")
            return redirect("add_new_subject")

        new_subject = Subject.objects.create(
            name       = name,
        )
        messages.success(request,"New Subject has been added")
        return redirect("subjects")
    return render(request, 'subject/add_new_subject.html')

@login_required
@permission_required('online_test.change_subject')
def edit_subject(request,pk):
    subject_object = get_object_or_404(Subject,id=pk)
    if request.method == "POST":
        name          = request.POST.get('name').strip()

        if subject_object.name != name:
            check_exist = Subject.objects.filter(name__icontains=name).exists()
            if check_exist:
                messages.warning(request,"Subject Already exist!")
                return redirect("edit_subject",pk)

        new_subject = Subject.objects.filter(id=pk).update(
            name       = name,
        )
        messages.success(request,"Subject Successfully Updated")
        return redirect("subjects")
    subject_object = get_object_or_404(Subject,id=pk)
    context = {
        'data' : subject_object
    }
    return render(request, 'subject/edit_subject.html',context)

@login_required
@permission_required('online_test.view_subject')
def subjects(request):
    subjects = Subject.objects.all().order_by("-id")
    context = {
        "subjects" : subjects
    }
    return render(request,"subject/subjects.html",context=context)

@login_required
@permission_required('online_test.delete_subject')
def delete_subject(request,pk):
    subject = get_object_or_404(Subject,id=pk)
    subject.delete()
    messages.success(request,"Successfully subject deleted")
    return redirect("subjects")

@login_required
@permission_required('online_test.view_question')
def questions(request):
    subject_id = request.GET.get('subject_id')
    subjects = Subject.objects.all()

    if subject_id:
        questions = Question.objects.filter(subject_id=subject_id).order_by("-id")
    else:
        questions = Question.objects.all().order_by("-id")
        subjects = Subject.objects.all()

    context = {
        'questions': questions,
        'subjects': subjects,
        'selected_subject_id': subject_id
    }
    return render(request, 'question/questions_new.html', context)


@login_required
@permission_required('online_test.add_question')
def add_new_question(request):
    if request.method == "POST":
        right_mcq_option = None
        mcq_option1 = None
        mcq_option2 = None
        mcq_option3 = None
        mcq_option4 = None
        answer = None
        question_type = request.POST.get('question_type')
        question_level = request.POST.get('question_level')
        question = request.POST.get('question').strip()
        subject = request.POST.get('subject')

        check_exist = Question.objects.filter(question__icontains=question).exists()
        if check_exist:
            messages.warning(request,"Questions Already exist!")
            return redirect("add_new_question")

        if question_type == "MCQ":
            right_mcq_option = request.POST.get('right_mcq_option') if request.POST.get('right_mcq_option') else None
            mcq_option1 = request.POST.get('mcq_option1').strip() if request.POST.get('mcq_option1') else None
            mcq_option2 = request.POST.get('mcq_option2').strip() if request.POST.get('mcq_option2') else None
            mcq_option3 = request.POST.get('mcq_option3').strip() if request.POST.get('mcq_option3') else None
            mcq_option4 = request.POST.get('mcq_option4').strip() if request.POST.get('mcq_option4') else None

            if right_mcq_option == 'mcq_option1':
                right_mcq_option = "mcq_option1"
            elif right_mcq_option == 'mcq_option2':
                right_mcq_option = "mcq_option2"
            elif right_mcq_option == 'mcq_option3':
                right_mcq_option = "mcq_option3"
            elif right_mcq_option == 'mcq_option4':
                right_mcq_option = "mcq_option4"

        elif question_type == "Long Answer":
            answer = request.POST.get('answer').strip()

        new_question = Question.objects.create(
            right_mcq_option = right_mcq_option,
            question_type    = question_type,
            question_level   = question_level,
            mcq_option1      = mcq_option1,
            mcq_option2      = mcq_option2,
            mcq_option3      = mcq_option3,
            mcq_option4      = mcq_option4,
            question         = question,
            answer           = answer,
            subject_id       = subject
        )
        messages.success(request,"Successfully question has been added")
        return redirect("questions")

    subjects = Subject.objects.all().order_by('-id')
    
    context = {
        "subjects":subjects
    }
    return render(request, 'question/add_new_question.html',context)

@login_required
@permission_required('online_test.change_question')
def edit_question(request,pk):
    question_object = get_object_or_404(Question,id=pk)
    if request.method == "POST":
        right_mcq_option = None
        mcq_option1 = None
        mcq_option2 = None
        mcq_option3 = None
        mcq_option4 = None
        answer = None
        question_type = request.POST.get('question_type')
        question_level = request.POST.get('question_level')
        question = request.POST.get('question').strip()
        subject = request.POST.get('subject')

        if question_object.question != question:
            check_exist = Question.objects.filter(question__icontains=question).exists()
            if check_exist:
                messages.warning(request,"Questions Already exist!")
                return redirect("edit_question",pk)

        if question_type == "MCQ":
            right_mcq_option = request.POST.get('right_mcq_option') if request.POST.get('right_mcq_option') else None
            mcq_option1 = request.POST.get('mcq_option1').strip() if request.POST.get('mcq_option1') else None
            mcq_option2 = request.POST.get('mcq_option2').strip() if request.POST.get('mcq_option2') else None
            mcq_option3 = request.POST.get('mcq_option3').strip() if request.POST.get('mcq_option3') else None
            mcq_option4 = request.POST.get('mcq_option4').strip() if request.POST.get('mcq_option4') else None

            if right_mcq_option == 'mcq_option1':
                right_mcq_option = "mcq_option1"
            elif right_mcq_option == 'mcq_option2':
                right_mcq_option = "mcq_option2"
            elif right_mcq_option == 'mcq_option3':
                right_mcq_option = "mcq_option3"
            elif right_mcq_option == 'mcq_option4':
                right_mcq_option = "mcq_option4"

        elif question_type == "MCQ":
            answer = request.POST.get('answer').strip()

        update_question = Question.objects.filter(id=pk).update(
            right_mcq_option = right_mcq_option,
            question_type    = question_type,
            question_level   = question_level,
            mcq_option1      = mcq_option1,
            mcq_option2      = mcq_option2,
            mcq_option3      = mcq_option3,
            mcq_option4      = mcq_option4,

            question         = question,
            answer           = answer,
            subject_id       = subject
        )
        messages.success(request,"successfully question has been update")
        return redirect("questions")

    subjects = Subject.objects.all()
    question_object = get_object_or_404(Question,id=pk)
    context  = {
        'data' : question_object,
        "subjects" : subjects
    }
    return render(request, 'question/edit_question.html', context)


@login_required
@permission_required('online_test.delete_question')
def delete_question(request,pk):
    question = get_object_or_404(Question,id=pk)
    question.delete()
    return redirect("questions")

def loadQuestionAnswer(request,pk):
    question = Question.objects.filter(id=pk).first()
    answer = None
    if question.question_type =="MCQ":
        answer = question.right_mcq_option
    if question.question_type == "Long Answer":
        answer = question.answer
    data = {
        "answer" : answer
    }
    return JsonResponse(data=data)

@login_required
def exam(request):
    subject = Subject.objects.latest("id").pk
    questions = Question.objects.filter(subject=subject)

    examinee = Examinee.objects.filter(user=request.user).exists()
    if request.user.is_authenticated and examinee:
        examinee = Examinee.objects.filter(user=request.user).first()

        if examinee.has_completed_exam:
            messages.warning(request,"You have already participated")
            return redirect('exam_result')

        if request.method == 'POST':
            correct_answers = []
            incorrect_answers = []

            check_teacher = Teacher.objects.filter(id=request.user.id).exists()
            if check_teacher:
                messages.warning(request,"You can't participate to this exam")
                return redirect("index")

            for question in questions:
                answer = request.POST.get(str(f"question_{question.id}"))
                select_mcq = request.POST.get(f"btnradio_{question.id}")
                selected_answer_examinee = Examinee.objects.get(user=request.user)
                SelectedAnswer.objects.create(
                    examinee=selected_answer_examinee,
                    question=question,
                    selected_mcq_option=select_mcq if question.question_type == 'MCQ' else None,
                    selected_long_answer=answer if question.question_type == 'Long Answer' else None
                    )
                if question.question_type == 'MCQ':
                    if select_mcq == question.right_mcq_option:
                        correct_answers.append(question.id)
                if question.question_type == 'Long Answer':
                    if answer.lower().strip() == question.answer.lower().strip():
                        correct_answers.append(question.id)
                else:
                    incorrect_answers.append(question.id)

            score = (len(correct_answers) / len(questions)) * 100

            examinee.score = score
            examinee.has_completed_exam = True
            examinee.save()
            return redirect('exam_result')

    context = {'questions': questions}
    return render(request, 'exam.html',context)

@login_required
def exam_result(request):
    check_teacher = Teacher.objects.filter(user_id=request.user.id).exists()
    if check_teacher:
        messages.warning(request, "You are not allowed to see this page")
        return redirect("index")

    examinee = Examinee.objects.get(user=request.user)
    if not examinee.has_completed_exam:
        messages.warning(request, "You haven't attended the exam. Please attend the exam.")
        return redirect('exam')

    selected_answers = SelectedAnswer.objects.filter(
            examinee=examinee,
            question=OuterRef('pk'),
        ).order_by('-id')

    questions = Question.objects.all().annotate(
            selected_answer=Subquery(selected_answers.values('selected_mcq_option')[:1], output_field=CharField())
        ).annotate(
            long_answer=Subquery(selected_answers.values('selected_long_answer')[:1], output_field=CharField())
        )

    context = {
        'score': examinee.score,
        "examinee": examinee,
        "questions": questions
        }
    return render(request, 'exam_result.html', context)

@login_required
@permission_required('online_test.delete_question')
def send_mail_to_subscriber(request):
    latest_subject = Subject.objects.last()
    
    subject = 'New Subject Announcement'
    html_message = render_to_string('email/new_subject_announcement.html', {'subject': latest_subject})
    plain_message = strip_tags(html_message)

    subscribers = Subscriber.objects.all()
    recipient_list = [subscriber.email for subscriber in subscribers]
    from_email = settings.DEFAULT_FROM_EMAIL

    send_mail(subject, plain_message, from_email, recipient_list, html_message=html_message)
    return redirect("dashboard")

@login_required
@permission_required('online_test.delete_question')
def get_subscriber(request):
    if request.method == "POST":
        email = request.POST.get('email')
        check_email = Subscriber.objects.filter(email=email).first()
        if check_email:
            messages.success(request, 'You are already subscribed!')
        else:
            Subscriber.objects.create(email=email)
            messages.success(request,"Successfully subscribe to our website")
            return redirect("index")