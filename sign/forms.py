from django import forms
from django.forms import ModelForm, widgets
from sign.models import Event, Guest
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import NON_FIELD_ERRORS
import re

#优化：子类表单化
#多继承 删除继承None的内容 置位NONE  name = NONE’
#继成nav导航

#需求：
#表格bootstrap-table 表格排序
#分页 允许跳页 首页 尾页 bootstrap分页实现
#嘉宾和发布会的修改 删除 ；批量导入和批量导出
#数据正则限制
#签到页风格

class AddEventForm(forms.Form):
	error_css_class = 'error'
	required_css_class = 'required'
	def limits(value):
		if value < 50 or value > 65535:
				raise ValidationError(
					_('%(value)s 不合法，发布会上限人数应该在50-65535'),
					params={'value': value},
				)
	
	name = forms.CharField(
		max_length=50,
		min_length=2,
		error_messages={
            'required':'用户名不能为空',
            'max_length':'最大长度不得超过50个字符',
            'min_length':'最小长度不得少于2个字符',
        },
		
		widget=forms.TextInput(
			attrs={
                'class': "form-control",
                'placeholder': u'名字',
            }
        ),
		help_text = "name "
		
	)

	limit = forms.IntegerField(
		validators=[limits],
		widget=forms.NumberInput(
			attrs={
				'class':'form-control',
				'placeholder':u'发布会最大人数',
			}
		),
		help_text = "limit "
	)
	#limit.widget.attrs.update(size='10')

	address = forms.CharField(
		max_length=200,
		min_length=5,
		widget=forms.TextInput(
			attrs={
				'class':'form-control',
				'placeholder':u'发布会所在地址',
			}
		),
		error_messages={
			'required':"地址不能为空",
			'max_length':'超过最长200字符',
			'min_length':'不能少于5字符',
		},
		help_text = "address "
	)
	start_time = forms.DateTimeField(
			widget=forms.DateTimeInput(
				attrs={
					'class':'form-control',
					'placeholder':'发布会举办日期',
					'type':'date'
				}
			),
			error_messages={
				'required': "日期不能为空",
				'invalid': '非法日期',
			},
			help_text = "start_time "
	)
	
	status = forms.BooleanField(required=False)
	
	def __init__(self, *args, **kwargs):
		super(AddEventForm, self).__init__(*args, **kwargs)
		a = Event.objects.all().values_list('name', 'address')
	
class AddGuestForm(forms.ModelForm):
	def phone_filed(phone):
		phone_re = re.compile(r'^(13[0-9]|15[012356789]|17[678]|18[0-9]|14[57])[0-9]{8}$')
		
		if not phone_re.match(phone):
			raise ValidationError(
				_('%(value)s 不是合法的手机号'),
				params={'value' : phone}
			)
			
	phone = forms.CharField(
		validators=[phone_filed],
		widget=forms.TextInput(
				attrs = {
					
					'class':'form-control',
					'placeholder':u'手机号',
				}
		),
		error_messages={
			'required':'不能为空'
		},
		label =  _('手机'),
        help_text = _('您的手机号码'), 
		
	)
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		#初始化字段属性
		self.fields['phone'].widget.attrs.update(size='40')
		self.fields['email'].widget.attrs.update({'size':'40'})

	
	class Meta:
		css = {
				'all': ('/css/test.css',),
			 }
		error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together': "%(model_name)s's %(field_labels)s are not unique.",
            }
        }
		model = Guest
		exclude = ['create_time']
		fields = '__all__'
		#loacl field
		#localized_fields = ('birth_date',) 
		#fields = ['event', 'realname', 'phone', 'email', 'sign']
		widgets = {
			'realname': forms.TextInput(
				attrs = {
					'class': 'form-control',
					'size': '40',
					'placeholder': u'姓名',
				},
			),

			'email':forms.EmailInput(
				attrs = {
					'class':'form-control',
					'placeholder':u'邮箱',
				}
			),
			
		}
		labels = {
			'event':_('发布会'),
            'realname': _('姓名'),
			'email': _('电子邮箱'), 
        }
		help_texts = {
			'event':_('发布会上限人数在50-65535'),
			'realname': _('你的名字'),
			'email': _('您的电子邮箱'), 
		}
		error_messages={
				'realname':{
					'required':"不能为空",
					'max_length':'最长16字符',
				},
		
				'email':{
					'required':"不能为空",
					'invalid':'格式不正确',
				},
			
		}
		