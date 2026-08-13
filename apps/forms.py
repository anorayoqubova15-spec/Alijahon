import re

from django.contrib.auth import forms, login
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import F
from django.forms import ModelForm, CharField, Form

from apps.models import User, Flow, Favorite, Transaction, Order, History, Product


# class UserModelForm(ModelForm):
#     confirm_password=CharField(max_length=50)
#     class Meta:
#         model = User
#         fields=['phone_number','password','confirm_password']
#     def clean_password(self):
#         password=self.cleaned_data['password']
#         if len(password)<3:
#             raise ValidationError("Password must be at least 3 characters")
#         hash_password=make_password(password)
#         return hash_password
#     def clean_phone_number(self):
#         phone_number=self.cleaned_data['phone_number']
#         phone_number=re.sub(r'\D','',phone_number)
#         return phone_number
#     def clean_confirm_password(self):
#         confirm_password=self.cleaned_data['confirm_password']
#         password=self.data['password']
#         if confirm_password != password:
#             raise ValidationError("Passwords do not match")
#
# class LoginForm(ModelForm):
#     class Meta:
#         model = User
#         fields = ['phone_number', 'password']
#
#     def __init__(self, *args, **kwargs):
#         self.request = kwargs.pop('request')
#         super().__init__(*args, **kwargs)
#
#     def clean(self):
#         phone_number = self.cleaned_data['phone_number']
#         phone_number = re.sub(r'\D', "", phone_number)
#         password = self.cleaned_data['password']
#
#         user_data = User.objects.filter(phone_number=phone_number).first()
#         if not user_data:
#             raise ValidationError("BUndey raqam mavjud emas")
#         if not check_password(password, user_data.password):
#             raise ValidationError("Parol xato kiritildi")
#
#         login(self.request, user_data)


# class LoginForm(ModelForm):
#     class Meta:
#         model = User
#         fields = ['phone_number', 'password']
#
#     def __init__(self, *args, **kwargs):
#         self.request = kwargs.pop('request')
#         super().__init__(*args, **kwargs)
#
#     def clean(self):
#         phone_number = self.cleaned_data['phone_number']
#         phone_number = re.sub(r'\D', "", phone_number)
#         password = self.cleaned_data['password']
#
#         user_data = User.objects.filter(phone_number=phone_number).first()
#         if not user_data:
#             raise ValidationError("BUndey raqam mavjud emas")
#         if not check_password(password, user_data.password):
#             raise ValidationError("Parol xato kiritildi")
#
#         login(self.request, user_data)

class LoginForm(Form):
    def __init__(self, *args, request=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.request = request

    phone_number = CharField(max_length=19)
    password = CharField(max_length=128)

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        phone_number = re.sub(r'\D', "", phone_number)

        queryset = User.objects.filter(phone_number=phone_number)

        if not queryset.exists():
            raise ValidationError('Bunday nomer yoq!')

        return phone_number

    def clean_password(self):
        password = self.cleaned_data['password']
        phone_number = self.cleaned_data.get('phone_number')

        queryset = User.objects.filter(phone_number=phone_number)
        if queryset.exists():
            user = queryset.first()
            if check_password(password, user.password):
                login(self.request, user)
            else:
                raise ValidationError('Parol xato!')


    # def clean_password(self):
    #     password = self.cleaned_data.get('password')
    #     phone_number = self.cleaned_data.get('phone_number')
    #
    #     if not phone_number:
    #         # phone_number allaqachon clean_phone_number da xato bergan
    #         return password
    #
    #     queryset = User.objects.filter(phone_number=phone_number)
    #     if queryset.exists():
    #         user = queryset.first()
    #         if check_password(password, user.password):
    #             login(self.request, user)
    #         else:
    #             raise ValidationError('Parol xato!')
    #     return password

class RegisterForm(ModelForm):
    conf_password = CharField(max_length=55)

    class Meta:
        model = User
        fields = ['phone_number', 'password', 'conf_password']

    def clean_password(self):
        password = self.cleaned_data['password']
        hash_password = make_password(password)
        return hash_password

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        user_data = User.objects.filter(phone_number=phone_number).first()
        if user_data:
            raise ValidationError("Bundey raqam allaqachon mavjud")
        phone_number = re.sub(r'\D', "", phone_number)
        return phone_number

    def clean_conf_password(self):
        conf_password = self.cleaned_data['conf_password']
        password = self.data['password']
        if conf_password != password:
            raise ValidationError("Conf pasrol xato kiritildi")


# class FlowForm(ModelForm):
#     class Meta:
#         model = Flow
#         fields = ['title', 'discount']
#
#     def __init__(self, *args, **kwargs):
#         self.product = kwargs.pop('product')
#         super().__init__(*args, **kwargs)
#
#     def clean(self):
#         discount = self.cleaned_data.get('discount')
#         pro_dis = self.product.payment
#
#         if discount > pro_dis:
#             raise ValidationError(
#                 "Siz kiritgan chegirma mahsulot uchun belgilangan summadan katta iltimos kichik kirriting")


class FlowForm(ModelForm):
    class Meta:
        model = Flow
        fields = ['title', 'discount', 'user', 'product']

    def clean_discount(self):
        discount = self.cleaned_data['discount']
        product = Product.objects.filter(id=int(self.data['product'])).first()

        discount = product.price - discount

        if discount < product.payment:
            raise ValidationError('Chegirma tolovdan katta bolishi mumkin emas!')
        return discount


class ProfileForm(ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'city', 'tg_id', 'description']


class FavModelForm(ModelForm):
    class Meta:
        model = Favorite
        fields = ['user', 'product']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')

        if self.user and product:
            favorite_qs = Favorite.objects.filter(user=self.user, product=product)

            if favorite_qs.exists():
                favorite_qs.delete()
                self.is_removed_action = True
                raise ValidationError("Product ochirildi.")

        return cleaned_data


class TransactionModelForm(ModelForm):
    class Meta:
        model = Transaction
        fields = ['user', 'account_number', 'amount', 'sms']

    def clean_amount(self):
        amount = self.cleaned_data['amount']

        User.objects.filter(pk=int(self.data['user'])).update(balance=F('balance') - amount)

        return amount


class OrderModelForm(ModelForm):
    class Meta:
        model = Order
        fields = ['quantity', 'flow', 'full_name', 'phone_number', 'product', 'comment', 'status', 'delivery_date',
                  'city']


class HistoryModelForm(ModelForm):
    class Meta:
        model = History
        fields = ['user', 'request']
