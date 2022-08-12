from django.contrib import admin
import decimal
from django import forms
# Register your models here.
from .models import Topic, Course, Student, Order
# Register your models here.
class CourseInline(admin.TabularInline):
    model = Course

class TopicAdmin(admin.ModelAdmin):
    inlines = [CourseInline]
    list_display=('name', 'length')
    def length(self, obj):
        return len(obj.name)

@admin.action(description='Reduce Price by 10 percent')
def reducePrice(modeladmin, request, queryset):
    
    for course in queryset:
        course.price = course.price * decimal.Decimal('0.9')
        course.save()
        
    

class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'for_everyone', 'description')
    actions = [reducePrice, ]


class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_name', ]
    filter_horizontal = ['interested_in', ]

admin.site.register(Topic, TopicAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Order)

