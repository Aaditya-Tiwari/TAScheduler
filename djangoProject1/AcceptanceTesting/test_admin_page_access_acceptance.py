from django.test import TestCase, Client

from djangoProject1.MethodFiles.GeneralMethods import CheckPermission
from djangoProject1.models import User

class TestAdminPageAcceptance(TestCase):
    def setUp(self):
        self.donkey = Client()
        self.admin = User(username='admin', role='Admin')
        self.instructor = User(username='instructor', role='Instructor')
        self.ta = User(username='ta', role='TA')
        self.admin.save()
        self.instructor.save()
        self.ta.save()

    def test_admin_access(self):
        response = self.donkey.post('/',{"username" : "admin", "password" : "Default_Password"}, follow=True)
        response = self.donkey.get('/admin_home.html')

        #redirects to the admin page
        self.assertTemplateUsed(response, "admin_home.html")

    def test_instructor_access(self):
        self.donkey.post('/', {"username": "instructor", "password": "Default_Password"}, follow=True)
        response = self.donkey.get('/admin_home.html')
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.context)
        self.assertEqual(response.context["message"], "You cannot access the Admin page.")
        self.assertTemplateUsed(response, "home.html")

    def test_ta_access(self):
        self.donkey.post('/', {"username": "ta", "password": "Default_Password"}, follow=True)
        response = self.donkey.get('/admin_home.html')

        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.context)
        self.assertEqual(response.context["message"], "You cannot access the Admin page.")
        self.assertTemplateUsed(response, "home.html")

    def test_no_user_access(self):
        response = self.donkey.get('/admin_home.html')

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')
