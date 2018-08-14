from django.db import models

# Create your models here.
#发布会表
class Event(models.Model):
	name = models.CharField(max_length=100)
	limit = models.IntegerField()
	status = models.BooleanField()
	address = models.CharField(max_length=200)
	start_time = models.DateTimeField('events time')
	create_time = models.DateTimeField(auto_now=True)
	numbers = models.IntegerField()
	#guest = models.ForeignKey(Guest, 'on_delete=models.CASCADE,')

	def __str__(self):
		return self.name
	class Meta:
		
		verbose_name = '发布会'
		verbose_name_plural = verbose_name



#嘉宾表
class Guest(models.Model):
	event = models.ForeignKey(Event, on_delete=models.CASCADE) #关联发布会id
	realname = models.CharField(max_length=16)
	phone = models.CharField(verbose_name="手机",max_length=11)
	email = models.EmailField()
	sign = models.BooleanField()
	create_time = models.DateTimeField(auto_now=True)
	
	class Meta:
		
		unique_together = ("event", "phone")
		ordering = ['-id']  #降序 ;'-id'升序
		verbose_name = '嘉宾'
		verbose_name_plural = verbose_name
		
	def __str__(self):
		return self.realname