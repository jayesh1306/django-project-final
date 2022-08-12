
import decimal

from django.db import models

# Create your models here.
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
# Create your models here.

def validate_price(value):
    if value < 50 or value > 500:
        raise ValidationError(
            _('%(value)s is not in allowed range'),
            params={'value': value},
        )
class Topic(models.Model):
    name = models.CharField(name="name", max_length=200)
    category = models.CharField(name="category" , max_length=100, default="Development")

    def __str__(self):
        return f"Topic(name = {self.name}, category = {self.category})"

class Course(models.Model):
    topic = models.ForeignKey(Topic, related_name='courses', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[validate_price])
    for_everyone = models.BooleanField(default=True)
    description = models.TextField(max_length=300, null=True, blank=True)
    interested = models.PositiveIntegerField(default=0)
    stages = models.PositiveIntegerField(default=3)

    def discount(self):
        self.price = decimal.Decimal(0.90) * self.price

    def __str__(self):
        return f"Course (name= {self.name}, price = {self.price}, for_everyone = {self.for_everyone}" \
               f"description={self.description})"

class Student(models.Model):
    Image = models.ImageField(upload_to=None, height_field=None, width_field=None, blank = True, null = True)
    student_name = models.CharField(max_length=100)
    CITY_CHOICES = [('WS', 'Windsor'), ('CG', 'Calgery'), ('MR', 'Montreal'), ('VC', 'Vancouver')]
    school = models.CharField(max_length=50, null=True, blank=True)
    city = models.CharField(max_length=2, choices=CITY_CHOICES, default='WS')
    interested_in = models.ManyToManyField(Topic)

    class Meta:
        permissions = [
            ("canSeeMyAccount", "Can see the my account page"),
            {"canSeeMyOrders", "Can see the placed orders"}
        ]

    def __str__(self):
        return f"Student(name = {self.student_name}, city= {self.city}), school = {self.school}"

class Order(models.Model):
    course = models.ForeignKey(Course, related_name="courses", on_delete=models.CASCADE)
    Student = models.ForeignKey(Student, related_name="students", on_delete=models.CASCADE)
    levels = models.IntegerField(default=1)
    order_date = models.DateTimeField(default=timezone.now)
    ORDER_CHOICES = [('0', 'Cancelled'), ('1', 'Order Confirmed')]
    order_status = models.CharField(max_length=2, choices=ORDER_CHOICES, default='0')
    def __str__(self):
        return f"Order(levels = {self.levels}, order_date = {self.order_date}, order_status = {self.order_status})"

    def total_cost(self):
        sum = 0
        for course in self.course:
            sum += course.price
        return sum