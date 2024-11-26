from django.shortcuts import render, redirect
from django.views import View

from djangoProject1.MethodFiles.Administrator import CreateCourse, CreateUser
from djangoProject1.models import User, Course, Lab

#this is for when we log in we have the current user
curUser = None

class LoginPage(View):
    def get(self, request):
        return render(request, "login.html", {})

    def post(self, request):
        #get the entered username and password in the form
        username = request.POST['username']
        password = request.POST['password']

        #filters to see if the user of the specified username is within the database
        user = User.objects.filter(username=username)

        #if we find a match then we proceed to check if the password matches
        if user.exists():
            #check for valid password, if valid then redirect to home page, if not then show the error message on login page
            if user[0].password == password:
                #if we have a match this stores the user's username this can be used to access the current user's data
                #in all the other pages using this: user = User.objects.filter(username=request.session['cur_user_name'])
                request.session['cur_user_name'] = user[0].username
                return redirect("home.html")
            else:
                message = "Username or Password is incorrect"
                return render(request, "login.html", {'message': message})

        #If we have an invalid username then print this message on the login page
        else:
            message = "User does not exist"
            return render(request, "login.html", {'message': message})



class ConfigureUserPage(View):
    def get(self, request):
        users = User.objects.all()
        return render(request, "configureUser.html", {"roles": User.ROLE_CHOICES, "users": users})

    def post(self, request):
        #filter to see which form is being accessed:
        form = request.POST.get('form_name')
        # Get the required fields for creating a user
        firstname = request.POST['first_name']
        lastname = request.POST['last_name']
        username = request.POST['username']
        password = request.POST['password']
        # course= request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone_number']
        role = request.POST['role']
        # course_name = request.POST['name']


        #Display users list:
        users = User.objects.filter(first_name=firstname, last_name=lastname, role=role,
                                    email=email, phone_number=phone)
        users_info = []
        for user in users:
            users_info.append({
                "firstname": user.first_name,
                "lastname": user.last_name,
                "role": user.role,
                "email": user.email,
                "phone_number": user.phone_number,
            })
        if form == "create_user":
            return self.addUserHelper(firstname, lastname, username, password, email, phone, role, request)
        elif form == "edit_user":
            return self.editUserHelper(firstname, lastname, username, password, email, phone, role, request)
        else:
            return render(request, "configureUser.html", {"roles": User.ROLE_CHOICES, "users": users_info})

    #helper class to enable the addition of user
    def addUserHelper(self, firstname, lastname, username, password, email, phone, role, request):
        # Get only the address since it is not requested in the post method
        address = request.POST['address']
        # course_name = request.POST['name']

        name = firstname + " " + lastname

        # Create user:
        user = CreateUser.create_user(firstname, lastname, username, password, email, phone, role, address)

        # Get all users to pass to the templateDesign
        all_users = User.objects.all()

        if user is None:
            return render(request, "configureUser.html", {
                "roles": User.ROLE_CHOICES,
                "users": all_users,
                'message': "Something went wrong when creating the user \"" + name + "\""})
        else:
            return render(request, "configureUser.html", {
                "roles": User.ROLE_CHOICES,
                "users": all_users,
                'message': "The user \"" + name + "\" has been created"})

    #Helper class to save/edit the user
    def editUserHelper(self,username,request):
        if request.method.get == "POST":
            user = User.objects.get(username=username)

            #Update user fields based on inputs:
            user.first_name = request.POST.get("first_name")
            user.last_name = request.POST.get("last_name")
            user.role = request.POST.get("role")
            user.courses = request.POST.get("courses")
            user.email = request.POST.get("email")
            user.phone_number = request.POST.get("phone_number")
            user.save()
            return redirect("configureUser.html.html")

class UserDirectoryPage(View):
    def get(self, request):
        users = User.objects.all()
        courses = Course.objects.all()
        return render(request, "user_Directory.html", {"users": users, "courses": courses})

    def post(self, request):
        return redirect('/home/')

class CourseDirectoryPage(View):
    def get(self, request):
        # Get the logged-in user
        current_username = request.session.get('cur_user_name')
        if not current_username:
            return redirect('/')  # Redirect to login if no user session exists

        user = User.objects.filter(username=current_username).first()
        if not user:
            return redirect('/')  # Redirect to login if user not found

        # Check for filtering in the query parameters
        filter_assigned = request.GET.get('filter') == 'assigned'

        # Default to all courses
        courses = Course.objects.all()

        # Apply filtering based on role
        if filter_assigned:
            if user.role == 'TA':
                # Get labs assigned to the TA and their parent courses
                labs = Lab.objects.filter(ta=user)
                courses = Course.objects.filter(labs__in=labs).distinct()
            elif user.role == 'Instructor':
                # Get courses assigned to the instructor
                courses = user.courses.all()

        return render(request, "course_Directory.html", {'courses': courses, 'user': user, 'filter_assigned': filter_assigned})

    def post(self, request):
        courses = Course.objects.all()
        return render(request, "course_Directory.html", {'courses': courses})

class HomePage(View):
    def get(self, request):
        return render(request, "home.html", {})

class AdminHomePage(View):
    def get(self, request):
        return render(request, "admin_Home.html", {})

class ConfigureCoursePage(View):
    def get(self, request):
        #make this into a method
        courses = Course.objects.all()
        instructors = User.objects.filter(role="Instructor")
        return render(request, "configureCourse.html", {"instructors": instructors, "courses": courses})

    def post(self, request):
        #this is to filter based on which form is being accessed
        form = request.POST.get('form_name')
        courses = Course.objects.all()
        #get the list of the instructors so that we can show it
        instructors = User.objects.filter(role="Instructor")

        if form == "create_course":
            return self.add_course_helper(courses, instructors, request)
        elif form == "create_lab":
            return self.add_lab_helper(courses, instructors, request)
        else:
            return render(request, "configureCourse.html",{"instructors": instructors,
                'courses':courses, 'message': "Something went wrong when fetching the form, please try again."})


    def add_course_helper(self, courses, instructors, request):
        # this gets the first and last name of the instructor as well as their role
        instructor_name = request.POST['instructor']

        # checks if the no instructor option was selected, course must be initialized with an instructor
        if instructor_name != "":
            # splits first and last name into 2 separate strings, also the role in () but that's not necessary here
            names = instructor_name.split(" ")
            instructor = User.objects.get(first_name=names[0], last_name=names[1])
        else:
            instructor = None

        # get the instructor by finding a user with the same first and last name
        # no need to filter role because the create_course method already does that
        cname = request.POST['course_name']

        course = CreateCourse.create_course(cname, instructor)
        if course is None:
            return render(request, "configureCourse.html", {"instructors": instructors,
                'courses': courses, 'message': "Something went wrong when creating the course \"" + cname + "\""})
        else:
            return render(request, "configureCourse.html", {"instructors": instructors,
                'courses': courses, 'message': "The course \"" + cname + "\" has been created"})


    def add_lab_helper(self, courses, instructors, request):
        return render(request, "configureCourse.html", {"instructors": instructors,
            'courses': courses, 'message': "Something went wrong when fetching the form, please try again."})