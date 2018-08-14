from django.contrib import admin
from sign.models import Event, Guest
# Register your models here.

class EventAdmin(admin.ModelAdmin):
	list_display = ['name', 'status', 'start_time', 'id']
	search_fields = ['name']
	list_fields = ['status']
class GuestAdmin(admin.ModelAdmin):
	list_display = ['realname', 'phone', 'email', 'sign', 
	'create_time', 'event']
	search_fields = ['realname', 'phone']
	list_fields = ['sign']
	
admin.site.register(Event, EventAdmin)
admin.site.register(Guest, GuestAdmin)

