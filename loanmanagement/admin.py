from django.contrib import admin
from .models import Person, Loan, Collector


# Register your models here.
class PersonAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'picture', 'document')


class CollectorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


admin.site.register(Person, PersonAdmin)
admin.site.register(Loan)
admin.site.register(Collector, CollectorAdmin)
