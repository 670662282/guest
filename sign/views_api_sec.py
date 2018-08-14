from django.http import JsonResponse, HttpResponse
from sign.models import Event, Guest
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.contrib import auth as django_auth
from Crypto.Cipher import AES 
import base64, time
import hashlib
import json


"""
  realize security regime  for interface(auth_base64, MD5 of timestamp and keys, AES)
  Base64 is an arbitrary binary to text string encoding method, 
  often used to transfer a small amount of binary data in the URL, Cookie, web page.
"""

# user_auth
def user_auth(request):
	# return ['Basic', 'XXXX']
	auth = request.META.get('HTTP_AUTHORIZATION', b'').split()
	try:
		#base64 decode return ['admin',  ':' , 'password' ]
		auth_parts = base64.b64decode(auth[1])
	except IndexError:
		return "null"
	userid, password = auth_parts[0], auth_parts[2]
	user = django_auth.authenticate(username=userid, password=password)
	
	if user is not None and user.is_active:
		django_auth.login(request, user)
		return 'success'
	else:
		return 'failure'
		
#get_event_list add user_auth
def get_event_list(request):

	auth_result = user_auth(request)
	if auth_result == " null":
		return JsonResponse({'status':10011, 'message':'user auth was None'})
	if suth_result ==  'failure':
		return JsonResponse({'status': 10012, 'message': 'user auth was failure'})


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
				event['status'] = r.status
				event['start_time'] = r.start_time
				event['numbers'] = r.numbers
				datas.append(event)
			return JsonResponse({'status': 200, 'message': 'success' ,'data':datas})
		else:
			return JsonResponse({'status':10022, 'message':'query result is empty'})	
			
			

#   md5 of timestamp and keys
def user_sign(request):
	if request.method == 'POST':
		client_time = request.POST.get('time', '')
		client_sign = request.POST.get('sign', '')
	else:
		return "error"
		
	if client_time == '' or client_sign == '':
		return "sign NONE"
		
	#get time Gap (s)
	server_time = str(time.time()).split('.')[0]
	
	time_gap = int(server_time) - int(client_time)
	if time_gap >= 60:
		return "auth timeout"
	
	#md5 client_time + '&Guest-Bugmaster'
	md5 = hashlib.md5()
	md5.update('{}&Guest-Bugmaster'.format(client_time).encode('utf-8'))
	if md5.hexdigest() != client_sign:
		return 'sign failure'
	else:
		return 'sign success'
		

		
# 添加发布会接口---增加签名+时间戳
def add_event(request):
	sign_result = user_sign(request)
	if sign_result == "error":
		return JsonResponse({'status':10011,'message':'request error'})
	elif sign_result == "sign NONE":
		return JsonResponse({'status':10012,'message':'user sign null'})
	elif sign_result == "auth timeout":
		return JsonResponse({'status':10013,'message':'user sign timeout'})
	elif sign_result == "sign failure":
		return JsonResponse({'status':10014,'message':'user sign error'})

	eid = request.POST.get('eid','')                 # 发布会id
	name = request.POST.get('name','')               # 发布会标题
	limit = request.POST.get('limit','')             # 限制人数
	status = request.POST.get('status','')           # 状态
	address = request.POST.get('address','')         # 地址
	start_time = request.POST.get('start_time','')   # 发布会时间

	if eid =='' or name == '' or limit == '' or address == '' or start_time == '':
		return JsonResponse({'status':10021,'message':'parameter error'})

	result = Event.objects.filter(id=eid)
	if result:
		return JsonResponse({'status':10022,'message':'event id already exists'})

	result = Event.objects.filter(name=name)
	if result:
		return JsonResponse({'status':10023,'message':'event name already exists'})

	if status == '':
		status = 1

	try:
		Event.objects.create(id=eid,name=name,limit=limit,address=address,status=int(status),start_time=start_time)
	except ValidationError:
		error = 'start_time format error. It must be in YYYY-MM-DD HH:MM:SS format.'
		return JsonResponse({'status':10024,'message':error})

	return JsonResponse({'status':200,'message':'add event success'})

	
	
# AES encode
#BS 只能16 24 32
BS = 16
#使长度 扩充到变成BS位 不利于传输 需要base64二次加密
#pad = lambda s : s + (BS - len(s) % BS ) * chr(BS - len(s) % BS)
#base64.urlsafe_b64encode(pad)

#还原成扩充前的
unpad = lambda s : s[0: - ord(s[-1])]

#Base64是把3个字节变为4个字节
#由于标准的Base64编码后可能出现字符+和/，
#在URL中就不能直接作为参数，所以又有一种"url safe"的base64编码，
#其实就是把字符+和/分别变成-和_：
def decryptBase64(src):
	return base64.urlsafe_b64decode(src)
	
def decryptAES(src, key):
	"""
	decode AES
	"""
	src = decryptBase64(src)
	
	#must len=16   
	iv = b'1172311105789011'
	cryptor = AES.new(key, AES.MODE_CBC, iv)
	text = cryptor.decrypt(src).decode()
	
	return unpad(text)
	
def aes_encryption(request):
	#len 16 24 32
	key = 'W7v4D60fds2Cmk2U'.encode('utf-8')
	if request.method == 'POST':
		data = request.POST.get('data', '')
	else:
		return 'error'
	
	if data == '':
		return 'data null'
	
	decode = decryptAES(data, key)
	
	return json.loads(decode)
	
	
	
# 嘉宾查询接口----AES算法
def get_guest_list(request):
    dict_data = aes_encryption(request)

    if dict_data == "data null":
        return JsonResponse({'status':10010,'message':'data null'})

    if dict_data == "error":
        return JsonResponse({'status':10011,'message':'request error'})

    # 取出对应的发布会id和手机号
    try:
        eid = dict_data['eid']
        phone = dict_data['phone']
    except KeyError:
        return JsonResponse({'status':10012,'message':'parameter error'})

    if eid == '':
        return JsonResponse({'status':10021,'message':'eid cannot be empty'})

    if eid != '' and phone == '':
        datas = []
        results = Guest.objects.filter(event_id=eid)
        if results:
            for r in results:
                guest = {}
                guest['realname'] = r.realname
                guest['phone'] = r.phone
                guest['email'] = r.email
                guest['sign'] = r.sign
                datas.append(guest)
            return JsonResponse({'status':200, 'message':'success', 'data':datas})
        else:
            return JsonResponse({'status':10022, 'message':'query result is empty'})

    if eid != '' and phone != '':
        guest = {}
        try:
            result = Guest.objects.get(phone=phone,event_id=eid)
        except ObjectDoesNotExist:
            return JsonResponse({'status':10022, 'message':'query result is empty'})
        else:
            guest['realname'] = result.realname
            guest['phone'] = result.phone
            guest['email'] = result.email
            guest['sign'] = result.sign
            return JsonResponse({'status':200, 'message':'success', 'data':guest})
	