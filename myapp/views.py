# Import necessary classes
# Import necessary classes
from curses.ascii import HT
from unicodedata import name
from django.http import HttpResponse, HttpResponseRedirect
from django.core.mail import send_mail
from .forms import OrderForm,InterestForm, RegisterForm
from .models import Topic, Course, Student, Order
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from datetime import datetime
from django.contrib.auth.models import Group
from django.conf import settings 

def index(request):
    top_list = Topic.objects.all().order_by('id')[:10]
    if 'last_login' in request.session:
        recent_login = request.session['last_login']
    else:
        recent_login = "Your last login was more than one hour ago"
    # We are passing context variable {'top_list': top_list}
    return render(request, 'myapp/index.html', {'top_list': top_list, 'recent_login': recent_login})


def about(request):
    # We are NOT passing any context variable here.
    about_visits = request.COOKIES.get('about_visits', "1")
    about_visits = int(about_visits) + 1
    
    response = render(request,'myapp/about.html', {'about_visits': about_visits})  # django.http.HttpResponse
    response.set_cookie(key='about_visits', value=about_visits)
    return response

def details(request, top_no):
    get_object_or_404(Topic, pk=top_no)
    top_courses = Topic.objects.filter(id=top_no)
    # We are passing context variable here which is top_courses. All the topics which are stored in top_courses are passed to detail0.html
    context = {
        'top_courses': top_courses[0].name,
        'courses': Course.objects.filter(topic=top_no)
    }
    return render(request, 'myapp/detail.html', context=context)

def courses(request):
    courlist = Course.objects.all().order_by('id')
    return render(request, 'myapp/courses.html', {'courlist': courlist})

def place_order(request):
    msg = ''
    courlist = Course.objects.all()
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if order.levels <= order.course.stages:
                order.save()
                if order.course.price > 150.00:
                    course = order.course
                    course.discount();
                    course.save()
                msg = 'Your course has been ordered successfully.'
            else:
                msg = 'You exceeded the number of levels for this course.'
            return render(request, 'myapp/order_response.html', {'msg': msg})
    else:
        form = OrderForm()
    return render(request, 'myapp/placeorder.html', {'form':form, 'msg':msg, 'courlist':courlist})

def coursedetail(request, cour_id):
    course = get_object_or_404(Course, pk=cour_id)
    if request.method == 'POST':
        form = InterestForm(request.POST)

        if form.is_valid() and form.cleaned_data['interested'] == '1':
                course.interested = course.interested + 1
                course.save()
                return redirect('/myapp')
    else:
        form = InterestForm()
    return render(request, 'myapp/coursedetail.html', {'form': form,'course': course})

def user_login(request):
    if request.method == 'POST':
        if request.session.test_cookie_worked():
            request.session.delete_test_cookie()
            print("Test cookie worked")
        else:
            print("Test cookie didn't work")
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                request.session['last_login'] = datetime.now().strftime("%H:%M:%S - %B %d, %Y")
                request.session.set_expiry(3600)
                #request.session.set_expiry(0)
                if request.GET.get('next') != None:
                    return redirect(request.GET.get('next'))
                else:
                    return HttpResponseRedirect(reverse('myapp:index'))
            else:
                return HttpResponse('Your account is disabled.')
        else:
            return HttpResponse('Invalid login details.')
    else:
        request.session.set_test_cookie()
        return render(request, 'myapp/login.html')


@login_required
def user_logout(request):
    #logout(request)
    request.session.flush()
    for key in list(request.session.keys()):
      del request.session[key]
    return HttpResponseRedirect(reverse(('myapp:index')))

@login_required(login_url='/myapp/login/')
def myaccount(request):
    user = None
    if request.user.has_perm("myapp.canSeeMyAccount"):
        user = request.user
        first_name = user.first_name
        last_name = user.last_name
        full_name = user.first_name+' '+user.last_name
        orders = Order.objects.filter(Student__student_name=full_name)
        topics = Student.objects.filter(student_name=full_name).values('interested_in__name')
        fname = request.user.first_name
        return render(request, 'myapp/my_account.html',
                      {"first_name": first_name, "last_name": last_name, "orders": orders, "topics": topics,
                       "fname": fname})
    else:
        return HttpResponse("You are not a registered student!")
    
def register(request):
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid(): 
                username = form.cleaned_data['UserName']
                password = form.cleaned_data['Password']
                isStudent = form.cleaned_data['IsStudent']
                email = form.cleaned_data['Email']
                firstName = form.cleaned_data['FirstName']
                lastName = form.cleaned_data['LastName']
                user = User.objects.create_user(username, email, password)
                user.save()
                user.first_name = firstName
                user.last_name = lastName
                user.save()
                print(isStudent)
                if int(isStudent) == 1:
                    print(isStudent)
                    my_group = Group.objects.get(name='Student') 
                    my_group.user_set.add(user)
                    print(user.username)
                return redirect('/myapp/login')
    else:
        form = RegisterForm()
        return render(request, 'myapp/register.html', {'form' : form})

@login_required
def myorders(request):
    if request.user.has_perm("myapp.canSeeMyOrders"):
        studentName = request.user.get_full_name()
        orders = Order.objects.filter(Student__student_name=studentName)
        if(orders.count() > 0):
            return render(request, 'myapp/myorders.html', {'orders' : orders})
        else:
            return HttpResponse("You have not placed any orders!")
    else:
        return HttpResponse("You need to be a student to see orders")

def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST.get('UserEmail')
        password = "new Password"
        user = User.objects.get(email = email)
        user.set_password(password)
        user.save()
        send_mail(
            subject="New Password", #subject
            message=password, #message
            from_email=settings.EMAIL_HOST_USER, #from
            recipient_list=[email], #to
        )
        return HttpResponse("We have emailed you a new password")
    else:
        return render(request, 'myapp/forgotPassword.html')
