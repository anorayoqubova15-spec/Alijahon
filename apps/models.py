from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db.models import CharField, TextField, DecimalField, BigIntegerField, Model, ImageField, ForeignKey, \
    CASCADE, DateTimeField, SET_NULL, TextChoices, IntegerField
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    def _create_user(self, phone_number, password, **extra_fields):
        if not phone_number:
            raise ValueError("Phone number kiritilishi shart")

        user = self.model(phone_number=phone_number, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        return self._create_user(phone_number, password, **extra_fields)

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser uchun is_staff=True bo‘lishi kerak")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser uchun is_superuser=True bo‘lishi kerak")

        return self._create_user(phone_number, password, **extra_fields)


class Region(Model):
    title = CharField(max_length=12)


class City(Model):
    title = CharField(max_length=12)
    region = ForeignKey('Region', on_delete=CASCADE, related_name='cities')


class User(AbstractUser):
    class RoleType(TextChoices):
        admin = 'admin', 'Admin'
        deliver = 'deliver', 'Deliver'

    username = None
    first_name = CharField(max_length=12, blank=True, null=True)
    last_name = CharField(max_length=12, blank=True, null=True)
    phone_number = CharField(max_length=19, unique=True)
    city = ForeignKey('City', on_delete=CASCADE, related_name='users', null=True, blank=True)
    tg_id = IntegerField(default=0, blank=True, null=True)
    description = TextField(default='', blank=True, null=True)
    api_key = CharField(max_length=11, default='')
    balance = DecimalField(decimal_places=2, max_digits=12, default=0)
    on_way = DecimalField(decimal_places=2, max_digits=12, default=0)
    role = CharField(choices=RoleType, default='')

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()



class Category(Model):
    name = CharField(max_length=55)
    photo = ImageField(upload_to='products/')


class Product(Model):
    title = CharField(max_length=155)
    price = DecimalField(max_digits=17, decimal_places=2)
    photo = ImageField(upload_to='products/')
    category = ForeignKey(Category, on_delete=CASCADE)
    description = TextField()
    stock = BigIntegerField()
    payment = DecimalField(max_digits=17, decimal_places=2, default=0.0)


class Flow(Model):
    title = CharField(max_length=155)
    discount = DecimalField(max_digits=17, decimal_places=2, default=0.0)
    user = ForeignKey(User, on_delete=CASCADE, related_name='flows')
    visits = IntegerField(default=0)
    product = ForeignKey(Product, on_delete=CASCADE, related_name='flows')
    created_at = DateTimeField(default=timezone.now)


class Order(Model):
    class StatusType(TextChoices):
        PACKING = 'packing', 'Packing'
        DELIVERING = 'delivering', 'Delivering'
        DELIVERED = 'delivered', 'Delivered'
        POSTPONED = 'postponed', 'Postponed'
        RETURNED = 'returned', 'Returned'
        CANCELLED = 'cancelled', 'Cancelled'
        HOLD = 'hold', 'Hold'
        ARCHIVE = 'archive', 'Archive'
        READY = 'ready', 'Ready'


    status = CharField(choices=StatusType, default=StatusType.PACKING)

    flow = ForeignKey('Flow', on_delete=CASCADE, related_name='orders', blank=True, null=True)
    product = ForeignKey('Product', on_delete=CASCADE, related_name='orders', blank=True, null=True)
    city = ForeignKey('User', on_delete=CASCADE, related_name='orders', blank=True, null=True)

    phone_number = CharField(max_length=19, default='', blank=True, null=True)
    full_name = CharField(max_length=255, default='', blank=True, null=True)
    quantity = IntegerField(default=1)
    comment = CharField(max_length=255, default='')

    created_at = DateTimeField(default=timezone.now)
    last_modified = DateTimeField(auto_now=True)
    delivery_date = DateTimeField(null=True, blank=True)


class Favorite(Model):
    user=ForeignKey(User, on_delete=CASCADE, related_name='favorites')
    product=ForeignKey(Product, on_delete=CASCADE, related_name='favorites')
    created_at = DateTimeField(default=timezone.now)

class Transaction(Model):
    class StatusType(TextChoices):
        SUCCESS = 'success', 'Success'
        ON_WAY = 'on_way', 'On Way'
        CANCELLED = 'cancelled', 'Cancelled'


    user = ForeignKey('User', on_delete=CASCADE, related_name='banks')

    account_number = IntegerField()
    amount = DecimalField(decimal_places=2, max_digits=12, default=0)
    status = TextField(choices=StatusType, default=StatusType.ON_WAY)
    sms = CharField(max_length=1219, default='')

    created_at = DateTimeField(auto_now_add=True)
class History(Model):
    user = ForeignKey('User', on_delete=CASCADE, related_name='history')
    request = CharField(max_length=255, default='')