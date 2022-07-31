from collections import defaultdict
import logging

import json

from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail, BadHeaderError
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from . import signals
from django.test import TestCase

from django.shortcuts import get_object_or_404, redirect, render
from django.template.response import TemplateResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from django.contrib import auth
from django.contrib.auth import authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import logout
from django.urls import reverse_lazy
from django.views import generic
# from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import HttpResponse, Http404, JsonResponse, HttpResponseBadRequest
# from .models import Customer, Profile
from toml.encoder import unicode

from .forms import TakeQuizForm, LearnerSignUpForm, InstructorSignUpForm, QuestionForm, BaseAnswerInlineFormSet, \
    UserForm, ProfileForm, PostForm, CourseForm
from django.http import HttpResponseRedirect, HttpResponse
from django.template import loader
from django.urls import reverse
from django.utils import timezone
from django.core import serializers
from django.conf import settings
import os
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import auth
from datetime import datetime, date
from django.core.exceptions import ValidationError
from . import models
import operator
import itertools
from django.db.models import Avg, Count, Sum, Q
from django.forms import inlineformset_factory
from .models import TakenQuiz, Profile, Quiz, Question, Answer, Learner, User, Course, Tutorial, Notes, Announcement, \
    Module, LearnerAnswer, Category, Module, Access
from django.db import transaction
from django.contrib.auth.hashers import make_password
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.forms import (AuthenticationForm, UserCreationForm,
                                       PasswordChangeForm, PasswordResetForm)

from django.contrib.auth import update_session_auth_hash
from elearn.functions import handle_uploaded_file

from bootstrap_modal_forms.generic import (
    BSModalLoginView,
    BSModalFormView,
    BSModalCreateView,
    BSModalUpdateView,
    BSModalReadView,
    BSModalDeleteView
)


# Shared Views

def home(request):
    return render(request, 'home.html')


def about(request):
    return render(request, 'about.html')


def services(request):
    return render(request, 'service.html')


def contact(request):
    return render(request, 'contact.html')


def login_form(request):
    return render(request, 'login.html')


def logoutView(request):
    logout(request)
    return redirect('home')


def loginView(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_active:
            auth.login(request, user)
            if user.is_admin or user.is_superuser:
                return redirect('dashboard')
            elif user.is_instructor:
                return redirect('instructor')
            elif user.is_learner:
                return redirect('learner')
            else:
                return redirect('login_form')
        else:
            messages.info(request, "Неправильный username или пароль")
            return redirect('login_form')


# Admin Views
def dashboard(request):
    user = User.objects.get(id=request.user.pk)
    if user.is_admin:
        course = Course.objects.all()
        users = User.objects.all().count()
        context = {'courses': course, 'users': users}

        return render(request, 'dashboard/admin/home.html', context)
    else:
        return render(request, 'dashboard/admin/error.html')


class AdminUserMixin(LoginRequiredMixin, UserPassesTestMixin):

    def test_func(self):
        user = User.objects.get(id=self.request.user.pk)
        return user.is_admin

    def handle_no_permission(self):
        return render(self.request, 'dashboard/admin/error.html')


class InstructorSignUpView(AdminUserMixin, CreateView):
    model = User
    form_class = InstructorSignUpForm
    template_name = 'dashboard/admin/signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'instructor'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        messages.success(self.request, 'Instructor Was Added Successfully')
        return redirect('isign')


class AdminLearner(AdminUserMixin, CreateView):
    model = User
    form_class = LearnerSignUpForm
    template_name = 'dashboard/admin/learner_signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'learner'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        messages.success(self.request, 'Ученик удачно добавлен')
        return redirect('addlearner')


def course(request):
    user = User.objects.get(id=request.user.pk)
    if user.is_admin:
        categorys = Category.objects.only('id', 'name')
        context = {'categorys': categorys}

        return render(request, 'dashboard/admin/course.html', context)
    else:
        return render(request, 'dashboard/admin/error.html')


def post_course(request):
    user = User.objects.get(id=request.user.pk)
    if user.is_admin:
        if request.method == 'POST':
            name = request.POST['name']
            if 'category_id' in request.POST:
                category_id = request.POST['category_id']
            else:
                category_id = None
            if 'cprice' in request.POST:
                cprice = request.POST['cprice']
            else:
                cprice = None

            synopsis = request.POST['synopsis']

            if 'thumb' in request.FILES:
                thumb = request.FILES['thumb']
            else:
                thumb = None
            trainer = request.POST['trainer']

            a = Course(name=name, cprice=cprice, synopsis=synopsis, thumb=thumb, trainer=trainer,
                       category_id=category_id)
            a.save()
            messages.success(request, 'Курс создан успешно')
            return redirect('course')
        else:
            return render(request, 'dashboard/admin/course.html')

    else:
        return render(request, 'dashboard/admin/error.html')


class ADeleteCourse(AdminUserMixin, SuccessMessageMixin, DeleteView):
    model = Course
    template_name = 'dashboard/admin/confirm_delete3.html'
    success_url = reverse_lazy('list_course')
    success_message = "Курс успешно удален"


class ListCourseView(AdminUserMixin, LoginRequiredMixin, ListView):
    model = Course
    template_name = 'dashboard/admin/list_course.html'
    context_object_name = 'courses'
    paginated_by = 10

    def get_queryset(self):
        return Course.objects.order_by('-id')


class course_detail(AdminUserMixin, generic.DetailView):
    model = Course
    template_name = 'dashboard/admin/course_detail.html'

    def get_context_data(self, **kwargs):
        module = Module.objects.filter(course=self.kwargs['pk'])
        tutorial = Tutorial.objects.filter(module=self.kwargs['pk'])
        context = super(course_detail, self).get_context_data(**kwargs)
        context['tutorials'] = tutorial
        context['modules'] = module
        return context


def update_course(request, pk):
    user = User.objects.get(id=request.user.pk)
    if user.is_admin:
        course = Course.objects.get(id=pk)
        categorys = Category.objects.all()
        template = loader.get_template('dashboard/admin/update_object.html')
        context = {
            'course': course,
            'categorys': categorys
        }
        return HttpResponse(template.render(context, request))
    else:
        return render(request, 'dashboard/admin/error.html')


def addcourse(request, pk):
    user = User.objects.get(id=request.user.pk)
    if user.is_admin:
        course = Course.objects.get(id=pk)
        if not course.is_shown:
            course.is_shown = True
            course.save()
            return redirect('list_course')
        else:
            return render(request, 'dashboard/admin/error.html')
    else:
        return render(request, 'dashboard/admin/error.html')


def updaterecord(request, pk):
    user = User.objects.get(id=request.user.pk)
    if user.is_admin:
        if 'name' in request.POST:
            name = request.POST['name']
        else:
            name = 'Java'
        if 'cprice' in request.POST:
            cprice = request.POST['cprice']
        else:
            cprice = 500
        if 'category_id' in request.POST:
            category_id = request.POST['category_id']
        else:
            category_id = None
        if 'synopsis' in request.POST:
            synopsis = request.POST['synopsis']
        else:
            synopsis = None

        if 'trainer' in request.POST:
            trainer = request.POST['trainer']
        else:
            trainer = None
        course = Course.objects.get(id=pk)
        course.name = name
        course.cprice = cprice
        course.synopsis = synopsis
        course.trainer = trainer

        course.category_id = category_id
        course.save()
        return render(request, 'dashboard/admin/home.html')
    else:
        return render(request, 'dashboard/admin/error.html')


class ListUserView(AdminUserMixin, LoginRequiredMixin, ListView):
    model = User
    template_name = 'dashboard/admin/list_users.html'
    context_object_name = 'users'
    paginated_by = 10

    def get_queryset(self):
        return User.objects.order_by('-id')


class AccessList(AdminUserMixin, LoginRequiredMixin, ListView):
    model = Access
    template_name = 'dashboard/admin/access.html'
    context_object_name = 'accesses'
    paginated_by = 10

    def get_queryset(self):
        return Access.objects.order_by('date')


def usercourse(request, pk):
    user = User.objects.get(id=request.user.pk)
    if user.is_admin:
        users = User.objects.get(id=pk)
        courses = Course.objects.only('id', 'name')
        context = {'courses': courses, 'users': users}

        return render(request, 'dashboard/admin/UserCourse.html', context)
    else:
        return render(request, 'dashboard/admin/error.html')


def courseu(request, pk):
    user = User.objects.get(id=request.user.pk)
    if user.is_admin:
        if request.method == 'POST':
            course = request.POST['course']
            a = User(id=pk)
            a.course_set.add(course)
            b = Course.objects.get(pk=course)
            c = Access(user=a, course=b)
            c.save()
            return redirect('aluser')
        else:
            messages.error(request, 'По неизвестной причине, курс не добавлен')
            return redirect('aluser')
    else:
        return render(request, 'dashboard/admin/error.html')


class ADeleteuser(AdminUserMixin, SuccessMessageMixin, DeleteView):
    model = User
    template_name = 'dashboard/admin/confirm_delete2.html'
    success_url = reverse_lazy('aluser')
    success_message = "Пользователь удачно удален"


def create_user_form(request):
    user = User.objects.get(id=request.user.pk)
    if user:
        return render(request, 'dashboard/admin/add_user.html')
    else:
        return render(request, 'dashboard/admin/home.html')


def create_user(request):
    user = User.objects.get(id=request.user.pk)
    if user:
        if request.method == 'POST':
            first_name = request.POST['first_name']
            last_name = request.POST['last_name']
            username = request.POST['username']
            email = request.POST['email']
            password = request.POST['password']
            password = make_password(password)

            a = User(first_name=first_name, last_name=last_name, username=username, password=password, email=email,
                     is_admin=True)
            a.save()
            messages.success(request, 'Admin Was Created Successfully')
            return redirect('aluser')
        else:
            messages.error(request, 'Admin Was Not Created Successfully')
            return redirect('create_user_form')
    else:
        return render(request, 'dashboard')


class ADeleteuser(AdminUserMixin, SuccessMessageMixin, DeleteView):
    model = User
    template_name = 'dashboard/admin/confirm_delete2.html'
    success_url = reverse_lazy('aluser')
    success_message = "Пользователь успешно удален"


def acreate_profile(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        birth_date = request.POST['birth_date']
        phonenumber = request.POST['phonenumber']
        city = request.POST['city']
        country = request.POST['country']
        avatar = request.FILES['avatar']
        hobby = request.POST['hobby']
        current_user = request.user
        user_id = current_user.id
        print(user_id)

        Profile.objects.filter(id=user_id).create(user_id=user_id, phonenumber=phonenumber, first_name=first_name,
                                                  last_name=last_name, hobby=hobby, birth_date=birth_date,
                                                  avatar=avatar,
                                                  city=city, country=country)
        messages.success(request, 'Профиль успешно создан')
        return redirect('auser_profile')
    else:
        current_user = request.user
        user_id = current_user.id
        users = Profile.objects.filter(user_id=user_id)
        users = {'users': users}
        return render(request, 'dashboard/learner/create_profile.html', users)


def auser_profile(request):
    current_user = request.user
    user_id = current_user.id
    users = Profile.objects.filter(user_id=user_id)
    users = {'users': users}
    return render(request, 'dashboard/learner/user_profile.html', users)


def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = User.objects.filter(Q(email=data))
            if associated_users.exists():
                for user in associated_users:
                    subject = "Password Reset Requested"
                    email_template_name = "password_reset_email.txt"
                    c = {
                        "email": user.email,
                        'domain': 'q-edu.kz',
                        'site_name': 'Quantum Education',
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        'token': default_token_generator.make_token(user),
                        'protocol': 'https',
                    }
                    email = render_to_string(email_template_name, c)
                    try:
                        send_mail(subject, email, 'erasylabdulla20@gmail.com', [user.email], fail_silently=False)
                    except BadHeaderError:
                        return HttpResponse('Invalid header found.')
                    return redirect("/password_reset/done/")
    password_reset_form = PasswordResetForm()
    return render(request=request, template_name="password_reset.html",
                  context={"password_reset_form": password_reset_form})


# Instructor Views
def home_instructor(request):
    learner = User.objects.filter(is_learner=True).count()
    instructor = User.objects.filter(is_instructor=True).count()
    course = Course.objects.all().count()
    users = User.objects.all().count()
    context = {'learner': learner, 'course': course, 'instructor': instructor, 'users': users}

    return render(request, 'dashboard/instructor/home.html', context)


class QuizCreateView(AdminUserMixin, CreateView):
    model = Quiz
    fields = ('course',)
    template_name = 'dashboard/instructor/quiz_add_form.html'

    def form_valid(self, form):
        tutorial = Tutorial.objects.get(pk=self.kwargs['pk'])
        quiz = form.save(commit=False)
        quiz.owner = self.request.user
        quiz.tutorial = tutorial
        quiz.save()
        messages.success(self.request, 'Куиз создан! Добавьте вопросы.')
        return redirect('quiz_change', quiz.pk)


class QuizUpdateView(AdminUserMixin, UpdateView):
    model = Quiz
    fields = ('course')
    template_name = 'dashboard/instructor/quiz_change_form.html'

    def get_context_data(self, **kwargs):
        kwargs['questions'] = self.get_object().questions.annotate(answers_count=Count('answers'))
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        return self.request.user.quizzes.all()

    def get_success_url(self):
        return reverse('quiz_change', kwargs={'pk', self.object.pk})


def question_add(request, pk):
    user = User.objects.get(id=request.user.pk)
    if user.is_admin:
        quiz = get_object_or_404(Quiz, pk=pk, owner=request.user)

        if request.method == 'POST':
            form = QuestionForm(request.POST)
            if form.is_valid():
                question = form.save(commit=False)
                question.quiz = quiz
                question.save()
                messages.success(request, 'Добавьте ответы к этому вопросу')
                return redirect('question_change', quiz.pk, question.pk)
        else:
            form = QuestionForm()

        return render(request, 'dashboard/instructor/question_add_form.html', {'quiz': quiz, 'form': form})
    else:
        return render(request, 'dashboard/admin/error.html')


def question_change(request, quiz_pk, question_pk):
    user = User.objects.get(id=request.user.pk)
    if user.is_admin:
        quiz = get_object_or_404(Quiz, pk=quiz_pk, owner=request.user)
        question = get_object_or_404(Question, pk=question_pk, quiz=quiz)

        AnswerFormatSet = inlineformset_factory(
            Question,
            Answer,
            formset=BaseAnswerInlineFormSet,
            fields=('text', 'is_correct'),
            min_num=2,
            validate_min=True,
            max_num=10,
            validate_max=True
        )

        if request.method == 'POST':
            form = QuestionForm(request.POST, instance=question)
            formset = AnswerFormatSet(request.POST, instance=question)
            if form.is_valid() and formset.is_valid():
                with transaction.atomic():
                    formset.save()
                    formset.save()
                messages.success(request, 'Вопрос и ответы сохранены')
                return redirect('quiz_change', quiz.pk)
        else:
            form = QuestionForm(instance=question)
            formset = AnswerFormatSet(instance=question)
        return render(request, 'dashboard/instructor/question_change_form.html', {
            'quiz': quiz,
            'question': question,
            'form': form,
            'formset': formset
        })
    else:
        return render(request, 'dashboard/admin/error.html')


class QuizListView(AdminUserMixin, ListView):
    model = Quiz
    ordering = ('name', 'course')
    context_object_name = 'quizzes'
    template_name = 'dashboard/instructor/quiz_change_list.html'

    def get_queryset(self):
        queryset = self.request.user.quizzes \
            .select_related('course') \
            .annotate(questions_count=Count('questions', distinct=True)) \
            .annotate(taken_count=Count('taken_quizzes', distinct=True))
        return queryset


class QuestionDeleteView(AdminUserMixin, DeleteView):
    model = Question
    context_object_name = 'question'
    template_name = 'dashboard/instructor/question_delete_confirm.html'
    pk_url_kwarg = 'question_pk'

    def get_context_data(self, **kwargs):
        question = self.get_object()
        kwargs['quiz'] = question.quiz
        return super().get_context_data(**kwargs)

    def delete(self, request, *args, **kwargs):
        question = self.get_object()
        messages.success(request, 'Вопрос успешно удален')
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        return Question.objects.filter(quiz__owner=self.request.user)

    def get_success_url(self):
        question = self.get_object()
        return reverse('quiz_change', kwargs={'pk': question.quiz_id})


class QuizResultsView(AdminUserMixin, DeleteView):
    model = Quiz
    context_object_name = 'quiz'
    template_name = 'dashboard/instructor/quiz_results.html'

    def get_context_data(self, **kwargs):
        quiz = self.get_object()
        taken_quizzes = quiz.taken_quizzes.select_related('learner__user').order_by('-date')
        total_taken_quizzes = taken_quizzes.count()
        quiz_score = quiz.taken_quizzes.aggregate(average_score=Avg('score'))
        extra_context = {
            'taken_quizzes': taken_quizzes,
            'total_taken_quizzes': total_taken_quizzes,
            'quiz_score': quiz_score
        }

        kwargs.update(extra_context)
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        return self.request.user.quizzes.all()


class QuizDeleteView(AdminUserMixin, DeleteView):
    model = Quiz
    context_object_name = 'quiz'
    template_name = 'dashboard/instructor/quiz_delete_confirm.html'
    success_url = reverse_lazy('quiz_change_list')

    def delete(self, request, *args, **kwargs):
        quiz = self.get_object()
        messages.success(request, 'The quiz %s was deleted with success!' % quiz.name)
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        return self.request.user.quizzes.all()


def question_add(request, pk):
    # By filtering the quiz by the url keyword argument `pk` and
    # by the owner, which is the logged in user, we are protecting
    # this view at the object-level. Meaning only the owner of
    # quiz will be able to add questions to it.
    quiz = get_object_or_404(Quiz, pk=pk, owner=request.user)
    user = User.objects.get(id=request.user.pk)
    if user.is_admin:
        if request.method == 'POST':
            form = QuestionForm(request.POST)
            if form.is_valid():
                question = form.save(commit=False)
                question.quiz = quiz
                question.save()
                messages.success(request, 'You may now add answers/options to the question.')
                return redirect('question_change', quiz.pk, question.pk)
        else:
            form = QuestionForm()

        return render(request, 'dashboard/instructor/question_add_form.html', {'quiz': quiz, 'form': form})
    return render(request, 'dashboard/admin/error.html')


class QuizUpdateView(AdminUserMixin, UpdateView):
    model = Quiz
    fields = ('name', 'course', 'tutorial')
    context_object_name = 'quiz'
    template_name = 'dashboard/instructor/quiz_change_form.html'

    def get_context_data(self, **kwargs):
        kwargs['questions'] = self.get_object().questions.annotate(answers_count=Count('answers'))
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        '''
        This method is an implicit object-level permission management
        This view will only match the ids of existing quizzes that belongs
        to the logged in user.
        '''
        return self.request.user.quizzes.all()

    def get_success_url(self):
        return reverse('quiz_change', kwargs={'pk': self.object.pk})


def user_profile(request):
    current_user = request.user
    user_id = current_user.id
    print(user_id)
    users = Profile.objects.filter(user_id=user_id)
    users = {'users': users}
    return render(request, 'dashboard/instructor/user_profile.html', users)


def create_profile(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        phonenumber = request.POST['phonenumber']
        bio = request.POST['bio']
        city = request.POST['city']
        country = request.POST['country']
        birth_date = request.POST['birth_date']
        avatar = request.FILES['avatar']
        current_user = request.user
        user_id = current_user.id
        thumb = request.FILES['thumb']

        print(user_id)

        Profile.objects.filter(id=user_id).create(user_id=user_id, first_name=first_name, last_name=last_name,
                                                  phonenumber=phonenumber, bio=bio, city=city, country=country,
                                                  birth_date=birth_date, avatar=avatar, thumb=thumb)
        messages.success(request, 'Profile was created successfully')
        return redirect('user_profile')
    else:
        current_user = request.user
        user_id = current_user.id
        print(user_id)
        users = Profile.objects.filter(user_id=user_id)
        users = {'users': users}
        return render(request, 'dashboard/instructor/create_profile.html', users)


def module(request):
    user = User.objects.get(id=request.user.pk)
    if user.is_admin:
        courses = Course.objects.only('id', 'name')
        context = {'courses': courses}

        return render(request, 'dashboard/admin/module.html', context)
    else:
        return render(request, 'dashboard/admin/error.html')


def publish_module(request):
    user = User.objects.get(id=request.user.pk)
    if user.is_admin:
        if request.method == 'POST':
            name = request.POST['name']
            course_id = request.POST['course_id']
            print(course_id)
            a = Module(name=name, course_id=course_id)
            a.save()
            messages.success(request, 'Модуль добавлен')
            return redirect('module')
        else:
            messages.error(request, 'Не удалось добавить модуль')
            return redirect('module')
    else:
        return render(request, 'dashboard/admin/error.html')


def tutorial(request, pk):
    user = User.objects.get(id=request.user.pk)
    if user.is_admin:
        modules = Module.objects.filter(id=pk)
        context = {'modules': modules}

        return render(request, 'dashboard/admin/tutorial.html', context)
    else:
        return render(request, 'dashboard/admin/error.html')


def publish_tutorial(request):
    user = User.objects.get(id=request.user.pk)
    if user.is_admin:
        if request.method == 'POST':
            title = request.POST['title']
            if 'module_id' in request.POST:
                module_id = request.POST['module_id']
            else:
                module_id = 1
            content = request.POST['content']
            current_user = request.user
            author_id = current_user.id
            if 'video' in request.POST:
                video = request.POST['video']
            else:
                video = None
            if 'task' in request.POST:
                task = request.POST['task']
            else:
                task = None

            print(author_id)
            print(module_id)
            a = Tutorial(title=title, content=content, user_id=author_id, module_id=module_id, video=video, task=task)
            a.save()
            messages.success(request, 'Урок успешно добавлен')
            return render(request, 'dashboard/admin/tutorial.html')
        else:
            messages.error(request, 'Не удалось добавить урок')
            return render(request, 'dashboard/admin/tutorial.html')
    else:
        return render(request, 'dashboard/admin/error.html')


class ITutorialDetail(AdminUserMixin, LoginRequiredMixin, DetailView):
    model = Tutorial
    template_name = 'dashboard/admin/tutorial_detail.html'

    def get_context_data(self, **kwargs):
        quiz = Quiz.objects.filter(tutorial=self.kwargs['pk'])
        context = super(ITutorialDetail, self).get_context_data(**kwargs)
        context['quizzes'] = quiz
        return context


def update_tutorial(request, pk):
    user = User.objects.get(id=request.user.pk)
    if user.is_admin:
        tutorial = Tutorial.objects.get(id=pk)
        template = loader.get_template('dashboard/admin/update_tutorial.html')
        context = {
            'tutorial': tutorial,
        }
        return HttpResponse(template.render(context, request))
    else:
        return render(request, 'dashboard/admin/error.html')


def updatetutor(request, pk):
    user = User.objects.get(id=request.user.pk)
    if user.is_admin:
        if 'title' in request.POST:
            title = request.POST['title']
        else:
            title = " "

        if 'content' in request.POST:
            content = request.POST['content']
        else:
            content = " "
        if 'thumb' in request.FILES:
            thumb = request.FILES['thumb']
        else:
            thumb = None
        if 'video' in request.POST:
            video = request.POST['video']
        else:
            video = None
        current_user = request.user
        author_id = current_user.id

        tutorial = Tutorial.objects.get(id=pk)
        tutorial.title = title
        tutorial.content = content
        tutorial.thumb = thumb
        tutorial.video = video
        tutorial.author_id = author_id
        tutorial.save()
        return redirect('list_course')
    else:
        return render(request, 'dashboard/admin/error.html')


# Learner Views
class ProfView(ListView):
    model = Course
    template_name = 'dashboard/learner/prof_courses.html'
    context_object_name = 'courses'

    def get_queryset(self):
        return Course.objects.filter(category__slug=1)


class ENT(ListView):
    model = Course
    template_name = 'dashboard/learner/prof_courses.html'
    context_object_name = 'courses'

    def get_queryset(self):
        return Course.objects.filter(category__slug=2)


class LearnerSignUpView(CreateView):
    model = User
    form_class = LearnerSignUpForm
    template_name = 'signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'learner'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        # return redirect('learner')
        return redirect('learner')


class ShopView(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'dashboard/learner/home.html'
    context_object_name = 'courses'
    paginated_by = 10

    def get_queryset(self):
        return Course.objects.filter(is_shown=True)


class scourse(generic.DetailView):
    model = Course
    template_name = 'dashboard/learner/course.html'

    def get_context_data(self, **kwargs):
        module = Module.objects.filter(course=self.kwargs['pk'])
        tutorial = Tutorial.objects.filter(module=self.kwargs['pk'])
        context = super(scourse, self).get_context_data(**kwargs)
        context['tutorials'] = tutorial
        context['modules'] = module
        return context


def ltutorial(request):
    tutorials = Tutorial.objects.all().order_by('-created_at')
    tutorials = {'tutorials': tutorials}
    return render(request, 'dashboard/learner/list_tutorial.html', tutorials)


def luser_profile(request):
    current_user = request.user
    user_id = current_user.id
    print(user_id)
    user = request.user
    taken_quiz = TakenQuiz.objects.get(learner=user)
    users = {'users': user, 'taken_quizzes': taken_quiz}
    return render(request, 'dashboard/learner/user_profile.html', users)


def lcreate_profile(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        phonenumber = request.POST['phonenumber']
        bio = request.POST['bio']
        city = request.POST['city']
        country = request.POST['country']
        birth_date = request.POST['birth_date']
        avatar = request.FILES['avatar']
        current_user = request.user
        user_id = current_user.id
        print(user_id)

        Profile.objects.filter(id=user_id).create(user_id=user_id, first_name=first_name, last_name=last_name,
                                                  phonenumber=phonenumber, bio=bio, city=city, country=country,
                                                  birth_date=birth_date, avatar=avatar)
        return redirect('luser_profile')
    else:
        current_user = request.user
        user_id = current_user.id
        print(user_id)
        users = Profile.objects.filter(user_id=user_id)
        users = {'users': users}
        return render(request, 'dashboard/learner/create_profile.html', users)


class LTutorialDetail(LoginRequiredMixin, DetailView):
    model = Tutorial
    template_name = 'dashboard/learner/tutorial_detail.html'


class Lesson(LoginRequiredMixin, DetailView):
    model = Tutorial
    template_name = 'dashboard/learner/lesson.html'

    def get_context_data(self, **kwargs):
        quiz = Quiz.objects.filter(tutorial=self.kwargs['pk'])
        context = super(Lesson, self).get_context_data(**kwargs)
        context['quizzes'] = quiz
        return context


class TakenQuizListView(ListView):
    model = TakenQuiz.objects.order_by('-pk')
    context_object_name = 'taken_quizzes'
    template_name = 'dashboard/learner/taken_quiz_list.html'

    def get_queryset(self):
        queryset = self.request.user.learner.taken_quizzes \
            .select_related('quiz', 'quiz__course') \
            .order_by('date').last()
        return queryset


class RatingTable(LoginRequiredMixin, DeleteView):
    model = TakenQuiz
    context_object_name = 'quiz'
    template_name = 'dashboard/learner/rating.html'

    def get_queryset(self):
        return self.request.qu


def take_quiz(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    learner = request.user.learner

    if learner.quizzes.filter(pk=pk).exists():
        LearnerAnswer.objects.filter(student=learner).delete()
        TakenQuiz.objects.filter(learner=learner, quiz=quiz).delete()

    total_questions = quiz.questions.count()
    unanswered_questions = learner.get_unanswered_questions(quiz)
    total_unanswered_questions = unanswered_questions.count()
    progress = 100 - round(((total_unanswered_questions - 1) / total_questions) * 100)
    question = unanswered_questions.first()

    if request.method == 'POST':
        form = TakeQuizForm(question=question, data=request.POST)
        if form.is_valid():
            with transaction.atomic():
                learner_answer = form.save(commit=False)
                learner_answer.student = learner
                learner_answer.save()
                if learner.get_unanswered_questions(quiz).exists():
                    return redirect('take_quiz', pk)
                else:
                    correct_answers = learner.quiz_answers.filter(answer__question__quiz=quiz,
                                                                  answer__is_correct=True).count()
                    score = round((correct_answers / total_questions) * 100.0, 2)
                    TakenQuiz.objects.create(learner=learner, quiz=quiz, score=score)
                    if score < 50.0:
                        messages.warning(request,
                                         'Постарайтесь в следующий раз! Ваш результат по тесту %s %s баллов' % (
                                             quiz.name, score))
                    else:
                        messages.success(request,
                                         'Поздравляем! Вы завершили тест %s с результатом %s баллов' % (
                                             quiz.name, score))
                    return redirect('taken_quiz_list')
    else:
        form = TakeQuizForm(question=question)

    return render(request, 'dashboard/learner/take_quiz_form.html', {
        'quiz': quiz,
        'question': question,
        'form': form,
        'progress': progress
    })


def buycourse(request, pk):
    user = User.objects.get(id=request.user.pk)
    if user.is_learner:
        return render(request, 'dashboard/learner/congrats.html')
    else:
        return render(request, 'dashboard/admin/list_course.html')


def showmycourses(request):
    user = User.objects.get(id=request.user.pk)
    if user.is_learner:
        courses = user.course_set.get_queryset()
        context = {'courses': courses}
        return render(request, 'dashboard/learner/mycourses.html', context)
    else:
        return render(request, 'dashboard')


def checkout(request, pk):
    course = Course.objects.get(id=pk)
    context = {'course': course}
    return render(request, 'dashboard/learner/checkout.html', context)


def paymentComplete(request, pk):
    Course.objects.get(id=pk)
    return render(request, 'dashboard/learner/congrats.html')
