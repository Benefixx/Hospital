from django.contrib import admin

from .models import ActionHistory, userProfile, CustomUser, Patient

class PatientAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'first_name', 'last_name',
         'patronymic', 'series', 'medical_number',
          'branch',
           'updated', 'chamber')
    search_fields = (
        'id', 'first_name', 'last_name',
         'patronymic', 'series', 'medical_number',
          'branch', 'last_create', 'updated', 'created', 'chamber')
    list_filter = ('last_create', 'updated', 'created')


admin.site.register(Patient, PatientAdmin)
admin.site.register(CustomUser)
admin.site.register(ActionHistory)