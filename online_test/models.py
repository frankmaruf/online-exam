from django.db import models
from django.contrib.auth.models import User


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class Subject(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Question(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    right_mcq_option = models.CharField(max_length=25, null=True , choices=(('mcq_option1', 'Option 1'), ('mcq_option2', 'Option 2'), ('mcq_option3', 'Option 3'), ('mcq_option4', 'Option 4')))
    question_type    = models.CharField(max_length=15, choices=(('MCQ', 'MCQ'), ('Long Answer', 'Long Answer')))
    question         = models.CharField(max_length=255)
    answer           = models.TextField(null=True)
    mcq_option1      = models.CharField(max_length=255,null=True)
    mcq_option2      = models.CharField(max_length=255, null=True)
    mcq_option3      = models.CharField(max_length=255, null=True)
    mcq_option4      = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.question

class Examinee(models.Model):
    has_completed_exam = models.BooleanField(default=False)
    user               = models.OneToOneField(User, on_delete=models.CASCADE)
    score              = models.DecimalField(max_digits=5, decimal_places=2,default=0)

    def __str__(self):
        return f"{self.user.username}'s total score {self.score}"

class SelectedAnswer(models.Model):
    examinee            = models.ForeignKey(Examinee, on_delete=models.CASCADE)
    question            = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_mcq_option = models.CharField(max_length=25, null=True, choices=(
        ('mcq_option1', 'Option 1'),
        ('mcq_option1', 'Option 2'),
        ('mcq_option1', 'Option 3'),
        ('mcq_option1', 'Option 4')
    ))
    selected_long_answer = models.TextField(null=True)

    def __str__(self):
        if self.question.question_type == 'MCQ':
            selected_answer = self.get_selected_mcq_option_display()
            correct_answer = self.question.get_right_mcq_option_display()
        else:
            selected_answer = self.selected_long_answer
            correct_answer = self.question.answer

        return f"{self.examinee.user.username}'s answer to '{self.question.question}' is '{selected_answer}', correct answer is '{correct_answer}'"
    
class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    
    def __str__(self) -> str:
        return f"{self.email}"