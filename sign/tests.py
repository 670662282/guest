from django.test import TestCase
from sign.models import Event, Guest
from django.contrib.auth.models import User

# Create your tests here.

class ModelTest(TestCase):
	def setUp(self):
		Event.objects.create(id=4, name="oneplus 3 event", status=True,
			limit=2000, address="shenzhen", start_time='2016-08-03 02:11:11', numbers=1)
		Guest.objects.create(event_id=1, realname='alen',
			phone=123232321, email='alen@maub.com', sign=False)
			
	def test_event_models(self):
		result = Event.objects.get(name="oneplus 3 event")
		self.assertEqual(result.address, "shenzhen")
		self.assertTrue(result.status)

	def test_guest_models(self):
		result = Guest.objects.get(realname='alen')
		self.assertEqual(result.phone, '123232321')
		self.assertFalse(result.sign)
		


class IndexPageTest(TestCase):
	"""测试登录状态"""
	def test_index_page(self):
		response = self.client.get('/index/')
		self.assertEqual(response.status_code, 200)
		self.assertTemplateUsed(response, 'index.html')
		
class LoginActionTest(TestCase):
	def setUp(self):
		User.objects.create_user('admin', 'admin@mail.com', 'admin123456')
	def test_login_action(self):
		"""测试添加用户"""
		user = User.objects.get(username='admin')
		self.assertEqual(user.username, 'admin')
		self.assertEqual(user.email, 'admin@mail.com')
	
	def test_username_password_null(self):
		"""用户名密码为空"""
		test_data = {'username' : '', 'password' : ''}
		response = self.client.post('/login_actions/', data=test_data)
		self.assertEqual(response.status_code, 200)
		self.assertIn(b"username or passwd is error", response.content)
	
	def test_username_password_error(self):
		"""用户名密码错误"""
		test_data = {'username' : 'admins', 'password' : '213'}
		response = self.client.post('/login_actions/', data=test_data)
		self.assertEqual(response.status_code, 200)
		self.assertIn(b"username or passwd is error", response.content)
		
	def test_login_success(self):
		test_data = {'username' : 'admin', 'password' : 'admin123456'}
		"""登录成功"""
		response = self.client.post('/login_actions/', data=test_data)
		#302重定向
		self.assertEqual(response.status_code, 302)
		
class  EventManageTest(TestCase):
	"""发布会管理"""
	def setUp(self):
		User.objects.create_user('admin', 'admin@mail', 'admin123456')
		Event.objects.create(name='xiaomi', limit=2000, address='beijing',
							status=1, start_time='2018-3-2 12:30:22', numbers=0)
		self.login_user = {'username' : 'admin', 'password' : 'admin123456'}
	def test_event_manage_success(self):
		""" 测试发布会 """
		response = self.client.post('/login_actions/', self.login_user)
		response = self.client.post('/event_manage/')
		
		self.assertEqual(response.status_code, 200)
		self.assertIn(b'xiaomi', response.content)
		self.assertIn(b'beijing', response.content)
	
	def test_event_manage_search_success(self):
		"""测试发布会搜索"""
		response = self.client.post('/login_actions/', data=self.login_user)
		response = self.client.post('/search_name/', {'name' : 'xiaomi'})
		
		self.assertEqual(response.status_code, 200)
		self.assertIn(b'xiaomi', response.content)
		self.assertIn(b'beijing', response.content)

class GuestManageTest(TestCase):
	"""嘉宾管理"""
	def setUp(self):
		User.objects.create_user('admin', 'admin@mail', 'admin123456')
		Event.objects.create(id=1,name='xiaomi', limit=2000, address='beijing',
							status=1, start_time='2018-2-3 12:22:22', numbers=0)
		Guest.objects.create(realname='adawang', phone=1234444, email='admin@123.com',
							sign=0, event_id=1)
		data_user = {'username' : 'admin', 'password' : 'admin123456'}
	def Guest_search_phone(self):
		"""嘉宾搜索"""
		response = self.client.post('/login_actions/', data= self.data_user)
		response = self.client.post('/serach_phone/', {'phone' : '1234444'})
		
		self.assertEqual(response.status_code, 302)
		self.assertIn(b'adawang', response.content)
		self.assertIn(b'1234444', response.content)
	def Guest_info(self):
		"""嘉宾信息"""
		response = self.client.post('/login_actions/', data = self.data_user)
		response = self.client.post('/guest_manage/')
		
		self.assertEqual(response.status_code, 200)
		self.assertIn(b'adawang', response.content)
		self.assertIn(b'1234444', response.content)
		
	
class SignGuestTest(TestCase):
	"""签到测试"""
	def setUp(self):
		User.objects.create_user('admin', 'admin@mail.com', 'admin123456')
		Event.objects.create(id=1, name='xiaomi', limit=2000, address='beijing',
							status=1, start_time='2018-2-3 12:32:22', numbers=1)
		Event.objects.create(id=2, name='xiaohui', limit=2000, address='beijing',
							status=1, start_time='2019-3-2 12:11:11', numbers=0)
							
		Guest.objects.create(realname='adawang', phone='123123', email='admin@123', sign=1, event_id=1)
		Guest.objects.create(realname='jiangcheng', phone='123456', email='aedmin@123', sign=0, event_id=2)
		
		self.login_user = {'username' : 'admin', 'password' : 'admin123456'}
		
	
	def test_phone_is_null(self):
		"""手机号为空"""
		response = self.client.post('/login_actions/', data = self.login_user)
		
		response = self.client.post('/sign_index_action/1/', {'phone' : ''})
		
		self.assertEqual(response.status_code , 200)
		self.assertIn(b"phone error", response.content)
	
	def test_phone_eventid_error(self):
		"""手机号或者发布会id错误"""
		response = self.client.post('/login_actions/', data = self.login_user)
		response = self.client.post('/sign_index_action/2/', {'phone' : '123123'})
		
		self.assertEqual(response.status_code , 200)
		self.assertIn(b"phone or id error!", response.content)
		
	def sign_success(self):	
		"""签到成功"""
		response = self.client.post('/login_actions/', data = self.login_user)
		response = self.client.post('/sign_index_action/2/', {'phone' : '123456'})
		self.assertEqual(response.status_code , 200)
		self.assertIn(b'user is seccess !', response.content)
		
	def sign_has(self):
		"""已经签到"""
		response = self.client.post('/login_actions/', data = self.login_user)
		response = self.client.post('/sign_index_action/1/', {'phone' : '123123'})
		self.assertEqual(response.status_code , 200)
		self.assertIn(b'user has  sign !', response.content)