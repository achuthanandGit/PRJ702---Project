from django.contrib import admin
from .models import Identify


class IdentifyAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'submitted', 'tank', 'population')
    list_filter = ('submitted',)
    ordering = ('imageId', 'username')
    readonly_fields = ('submitted',)

# Register your models here.
admin.site.register(Identify, IdentifyAdmin)
