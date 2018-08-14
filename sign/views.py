from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from sign.models import Event, Guest
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404
from sign.forms import AddEventForm, AddGuestForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db.models import Count

# Create your views here.
@login_required
def my_info(request):
	return render(request, 'my_info.html')


@login_required
def add_event(request):
	username = request.session.get('user', '')
	if request.method == 'POST':
		form = AddEventForm(request.POST)
		#emsg = form.errors
		if form.is_valid():
			name = form.cleaned_data['name']
			address = form.cleaned_data['address']
			limit = form.cleaned_data['limit']
			start_time = form.cleaned_data['start_time']
			status = form.cleaned_data['status']
			
			if status:
				status = 1
			else:
				status = 0
					
			#需要同名检测
			Event.objects.create(name=name, limit=limit, address=address, status=status, start_time=start_time, numbers=0)
			return render(request, "add_event.html", {"user": username, "form": form, "alert": "alert alert-success","success": "添加发布会成功!"})
		else:
			
			return render(request, 'add_event.html', {"user":username, "form":form, "alert":"alert alert-danger", "success":"添加发布会失败"})		
	else:
		form = AddEventForm()
	return render(request, "add_event.html", {"user":username, "form":form})
	
	
@login_required
def add_guest(request):
	username = request.session.get('user', '')
	if request.method == 'POST':
		form = AddGuestForm(request.POST)
		if form.has_changed():
			print("The following fields changed: %s" % ", ".join(form.changed_data))
			#form实例访问字段 label属性
			print(form.fields['realname'].label)
			
			#{{ form.as_table }}将它们渲染为包含在<tr> 标签中的表格单元格
			#{{ form.as_p }}将它们包装在<p>标签中
			#{{ form.as_ul }}将它们包装在<li>标签中
			#请注意，您必须自己提供周围<table>或<ul> 元素。
			print(form.as_p())
			#realname HTML
			print("=====")
			print(form['realname'])
			#数据
			print("data:"+form['realname'].data)
			#emsg = form.errors
			if form.is_valid():
				event = form.cleaned_data['event']
				realname = form.cleaned_data['realname']
				phone = form.cleaned_data['phone']
				#print(realname.getcontent('value'))
				email = form.cleaned_data['email']
				sign = form.cleaned_data['sign']
				
				if sign:
					sign = 1
				else:
					sign = 0
				Guest.objects.create(realname=realname, phone=phone, event=event, email=email, sign=sign)
				return render(request, "add_guest.html", {"user": username, "form": form, "alert": "alert alert-success", "success": "添加嘉宾成功!"})
			else:
				return render(request, 'add_guest.html', {"user":username, "form":form, "alert": "alert alert-danger", "success": "添加嘉宾失败!" })
		else:
			print('ada')
			pass
	else:
		form = AddGuestForm()
	return render(request, "add_guest.html", {"user":username, "form":form})
	

@login_required
def logout(request):
	auth.logout(request)
	return HttpResponseRedirect('/index/')


@login_required
def sign_index_action(request, event_id):
	event = get_object_or_404(Event, id=event_id)
	phone = request.POST.get('phone', '')
	print(phone)
	result = Guest.objects.filter(phone=phone)
	if not result:
		return render(request, 'sign_index.html', 
		{ 'event' : event, 'hint' : 'phone error!'})
	
	result = Guest.objects.filter(phone=phone, event_id=event_id)
	
	if not result:
		return render(request, 'sign_index.html', 
		{ 'event' : event, 'hint' : 'phone or id error!'})
		
	result = Guest.objects.get(phone=phone, event_id=event_id)
	if result.sign:
		return render(request, 'sign_index.html', 
		{ 'event' : event, 'hint' : 'user has  sign !'})
	else:
		Guest.objects.filter(phone=phone, event_id=event_id).update(sign='1')
		#ge = Guest.objects.get(phone=phone).event
		print(event_id)
		numbers = Event.objects.get(id=event_id).numbers
		print(numbers)
		numbers += 1
		Event.objects.select_for_update().filter(id=event_id).update(numbers=numbers)
		
		return render(request, 'sign_index.html', 
		{ 'event' : event, 'hint' : 'user is seccess !', 'guest' : result})


@login_required
def sign_index(request, event_id):
	event = get_object_or_404(Event, id=event_id)
	guest_list = Guest.objects.filter(event_id=event_id)
	guest_data = str(len(guest_list)) #总人数
	sign_data = 0
	for guest in guest_list:
		if guest.sign:
			sign_data += 1
	return render(request, 'sign_index.html', {'event' : event,
												'guest':guest_data,
                                               'sign':sign_data})

def index(request):
	return render(request, "index.html")
	
def login_actions(request):
	if request.method == 'POST':
		username = request.POST.get('username', '')
		password = request.POST.get('password', '')
		user = auth.authenticate(username=username, password=password)
		if user is not None:
			auth.login(request, user)
			request.session['user'] = username
			#路径重定向
			response = HttpResponseRedirect('/event_manage/')
			#response.set_cookie('user', username, 3600)
			return response
		else:
			return render(request, 'index.html', {'error': 'username or passwd is error'})
	else:
		return HttpResponse("hello adawang")
	
@login_required	
def event_manage(request):
	
	event_list = Event.objects.all() #查询所有发布会对象
	#username = request.COOKIES.get('user', '')
	username = request.session.get('user', '')
	all_numbers = event_list.aggregate(Count('id'))['id__count']
	print(Event.objects.values_list('name').annotate(Count('id')))
	return render(request, "event_manage.html", {"user": username, "events":event_list, "all_numbers":all_numbers})
	
@login_required	
def guest_manage(request):
	guest_list = Guest.objects.all() #查询所有嘉宾对象
	username = request.session.get('user', '')
	
	paginator = Paginator(guest_list, 9)
	#获取要显示的页数
	page = request.GET.get('page')
	try:
		contacts = paginator.page(page)
	except PageNotAnInteger:
		 # 如果页数不是整型, 取第一页.
		contacts = paginator.page(1)
	except EmptyPage:
		# 如果页数超出查询范围，取最后一页
		contacts = paginator.page(paginator.num_pages)
	
	if contacts.has_previous():
		print('previous' + str(contacts.previous_page_number()))
	else:
		print('no previous')	
	if contacts.has_next() :
		print('next' + str(contacts.next_page_number()))
	else:
		print('no next')
		
	return render(request, "guest_manage.html", {"user": username, "guests":contacts})
	
	
@login_required	
def search_name(request):
	username = request.session.get('user', '')
	search_name = request.GET.get("name", "")
	#模糊查询名字为search_name的对象
	event_list = Event.objects.filter(name__contains=search_name)
	if len(event_list) == 0:
		return render(request, "event_manage.html", {"user": username, "hint":"根据输入的`发布会名称`查询结果为空！"})
	return render(request, "event_manage.html", {"user": username, "events":event_list})

#bug
@login_required
def	search_guest_name(request):
	username = request.session.get('user', '')
	search_guest_name = request.GET.get("realname", "")
	guest_list = Guest.objects.filter(realname__contains=search_guest_name)
	if len(guest_list) == 0:
		return render(request, "event_manage.html", {"user": username, "hint":"根据输入的`发布会名称`查询结果为空！"})
	paginator = Paginator(guest_list, 5)
	page = request.GET.get('page')
	try:
		contacts = paginator.page(page)
	except PageNotAnInteger:
		contacts = paginator.page(1)
	except EmptyPage:
		contacts = paginator.page(paginator.num_pages)
		
	return render(request, "guest_manage.html", {"user": username, "guests":contacts})
 
	