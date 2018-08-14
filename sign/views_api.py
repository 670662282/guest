from django.http import JsonResponse
from sign.models import Event, Guest
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db.utils import IntegrityError
import time

def add_event(request):
	eid = request.POST.get('eid', '')
	name = request.POST.get('name', '')
	limit = request.POST.get('limit', '')
	status = request.POST.get('address', '')
	start_time = request.POST.get('start_time', '')
	numbers = request.POST.get('numbers', '')
	
	if eid == '' or name == '' or limit == '' or status == '' or start_time == '':
			return JsonResponse({'status': 10021, 'message': 'parameter error'})
	result = Event.objects.filter(id=eid)
	if result:
		return JsonResponse({'status': 100022, 'message': 'event id aready exist'})
	
	result = Event.objects.filter(name=name)
	if result:
		return JsonResponse({'status': 100023, 'message': 'event name aready exist'})
	if staus == '':
		staus = 1
	if numbers == '':
		numbers = 0
	
	try:
		Event.objects.create(id=eid, name=name, limit=limit, address=address,
			status = int(status), start_time=start_time, numbers=numbers)
	except ValidationError:
		error = 'start_time format error. It must be in YYYY-MM-DD HH:MM:SS format.'
		return JsonResponse({'status': 100024, 'message':'error'})
	
	return JsonResponse({'status':200, 'message': 'add event success'})



#嘉宾添加 add_guest
def add_guest(request):
	eid = request.POST.get('eid', '')
	realname = request.POST.get('realname', '')
	phone = request.POST.get('phone', '')
	email = request.POST.get('email', '')
	
	if eid == '' or realname == '' or phone == '' or email == '':
			return JsonResponse({'status': 10021, 'message': 'parameter error'})
	result = Event.objects.filter(id=eid)
	if result:
		return JsonResponse({'status': 100022, 'message': 'event id aready exist'})	
		
	status = Event.objects.get(eid).status
	if not status:
		return JsonResponse({'status':10023,'message':'event status is not available'})
		
	event_limit = Event.objects.get(id=eid).limit 
	guest_limit = Event.object.filter(event_id=eid)
	
	if len(guest_limit) >= event_limit:
		return JsonResponse({'status':10024,'message':'event number is full'})

	event_time = Event.objects.get(id=eid).start_time    # 发布会时间
	timeArray = time.strptime(str(event_time), "%Y-%m-%d %H:%M:%S")
	e_time = int(time.mktime(timeArray))
	
	now_time = str(time.time())   # 当前时间
	ntime = now_time.split(".")[0]
	n_time = int(ntime)

	if n_time >= e_time:
		return JsonResponse({'status':10025,'message':'event has started'})
	try:
		Guest.objects.create(realname=realname,phone=int(phone),email=email,sign=0,event_id=int(eid))
	except IntegrityError:
		return JsonResponse({'status':10026,'message':'the event guest phone number repeat'})
	return JsonResponse({'status':200, 'message': 'add guest success'})
	
#发布会查询 get_event_list
def get_event_list(request):
	eid = request.GET.get('eid', '')
	name = request.GET.get('name', '')
	
	if eid == '' and name == '':
		return JsonResponse({'status': 100021, 'message':'name and eid is null'})
		
		
	if eid != '':
		event = {}
		try:
			result = Event.objects.get(id=eid)
		except ObjectDoesNotExist:
			return JsonResponse({'status': 100022, 'message': 'query result is empty'})
		else:
			event['eid'] = result.id
			event['name'] = result.name
			event['limit'] = result.limit
			event['address'] = result.address
			event['status'] = result.status
			event['start_time'] = result.start_time
			event['numbers'] = result.numbers
			return JsonResponse({'status': 200, 'message': 'success' ,'data':event})
			
	if name != '':
		datas = []
		result = Event.object.filter(name_contains = name)
		if result:
			for r in result:
				event = {}
				event['eid'] = r.id
				event['name'] = r.name
				event['limit'] = r.limit
				event['address'] = r.address
				event['staus'] = r.staus
				event['start_time'] = r.start_time
				event['numbers'] = r.numbers
				datas.append(event)
			return JsonResponse({'status': 200, 'message': 'success' ,'data':datas})
		else:
			return JsonResponse({'status':10022, 'message':'query result is empty'})
			
			
# 嘉宾查询接口 get_guest_list

def get_guest_list(request):
	eid = request.GET.get('eid', '')
	phone = request.GEt.get('phone', '')
	
	if eid == '':
		return JsonResponse({'status': 100021, 'message':'eid is null'})
	if eid != '' and phone == '':
		datas = []
		result = Guest.object.filter(eid = eid)
		if result:
			for r in result:
				event = {}
				event['realname'] = r.realname
				event['phone'] = r.phone
				event['email'] = r.email
				event['sign'] = r.sign
				datas.append(event)
			return JsonResponse({'status': 200, 'message': 'success' ,'data':datas})
		else:
			return JsonResponse({'status':10022, 'message':'query result is empty'})
			
			
	if eid != '' and phone != '':
		guest = {}
		try:
			result = Guest.objects.get(phone=phone, eid=eid)
		except ObjectDoesNotExist:
			return JsonResponse({'status':10022, 'message':'query result is empty'})
		else:
			guest['realname'] = r.realname
			guest['phone'] = r.phone
			guest['email'] = r.email
			guest['sign'] = r.sign
			return JsonResponse({'status': 200, 'message': 'success' ,'data':guest})
			
			
# user_sign
def user_sign(request):
	eid = request.POST.get('eid', '')
	phone = request.POST.get('eid', '')
	
	if eid == "" or phone == "":
		return JsonResponse({'status':10021,'message':'parameter error'})
	
	try:
		result = Event.objects.get(event_id=eid)
	except Event.DoesNotExist:
		return JsonResponse({'status': 10022, 'message': 'event id null'})
		
	status = Event.objects.get(eid).status
	if result.status is False:
		return JsonResponse({'status': 10023, 'message': 'event status is not available'}) 
	
	event_time = Event.objects.get(id=eid).start_time     # 发布会时间
	timeArray = time.strptime(str(event_time), "%Y-%m-%d %H:%M:%S")
	e_time = int(time.mktime(timeArray))
	
	now_time = str(time.time())   # 当前时间
	ntime = now_time.split(".")[0]
	n_time = int(ntime)

	if n_time >= e_time:
		return JsonResponse({'status':10025,'message':'event has started'})
	
	result = Guest.objects.filter(phone=phone)
	if not result:
		return JsonResponse({'status':10025,'message':'user phone null'})
	else:
		#判定手机号和发布会id的对应关系
		for res in result:
			if res.event_id == int(eid):
				break
		else:
			return JsonResponse({'status': 10026, 'message': 'user did not participate in the conference'})
	
	result = Guest.objects.filter(phone=phone, event_id=eid)
	print(result.sign)
	if result.sign:
		return JsonResponse({'status':10027,'message':'user has sign in'})
	else:
		result.sign = True
		result.save()
		return JsonResponse({'status':200,'message':'sign success'})
	
			
				