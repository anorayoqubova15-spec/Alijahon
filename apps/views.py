from datetime import timedelta
from multiprocessing import context
from urllib import request

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView
from django.db.models import Sum, Q, Count
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import TemplateView, ListView, CreateView, FormView, DetailView, UpdateView, DeleteView
from django.views import View
from django.shortcuts import render, redirect

from django.contrib.auth.views import LoginView as BaseLoginView
from django.contrib.auth import authenticate, login
from apps.models import User, Flow, Order, Favorite, Region, City
from apps.forms import *
from apps.models import Product, Category

class AdminAccountViewList(TemplateView):
    template_name = 'admin_accaunt.html'

class HomeViewList(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['products'] = Product.objects.all()

        return context


class AdminViewList(TemplateView):
    template_name = 'base/admin_page_base.html'



class CategoryListView(TemplateView):
    template_name = 'category.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        cate_id = self.kwargs.get('pk')
        if cate_id:
            data['cate_name'] = Category.objects.filter(id=cate_id).first()
            data['pro_data'] = Product.objects.filter(category_id=cate_id)
        else:
            data['pro_data'] = Product.objects.all()
            data['cate_name'] = "Barchasi"
        data['cate_data'] = Category.objects.all()
        return data

class ProductDetailView(DetailView):
    queryset = Product.objects.all()
    template_name = 'product_detail.html'
    pk_url_kwarg = 'pk'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        id = self.request.GET.get('id')

        if id:
            context['flow'] = Flow.objects.filter(id=id).first()
            Flow.objects.filter(pk=id, product=self.object).update(visits=F('visits') + 1)


        return context







#
#
# class UserCreateView(CreateView):
#     queryset = User.objects.all()
#     form_class =UserModelForm
#     template_name = "home.html"
#     success_url = reverse_lazy('home')
#     def form_valid(self, form):
#         for error_message in form.errors.values():
#             messages.error(self.request, error_message)
#         return super().form_invalid(form)
#
#
#
# class CustomerCreateView(FormView):
#     form_class = LoginForm
#     template_name = "home.html"
#     success_url = reverse_lazy('home')
#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         kwargs["request"] = self.request
#         return kwargs


class LoginViewList(FormView):
    form_class = LoginForm
    template_name = 'home.html'
    success_url = reverse_lazy('accaunt')

    def form_valid(self, form):
        messages.success(self.request, 'Hush kelibsiz')
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs


class RegisterViewList(CreateView):
    form_class = RegisterForm
    template_name = 'home.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        messages.success(self.request, "Muffaqaiyati royxatdan otildi")
        return super().form_valid(form)

    def form_invalid(self, form):
        for error_messege in form.errors.values():
            messages.error(self.request, error_messege)
        return super().form_invalid(form)




class MarketView(ListView):
    queryset = Product.objects.all()
    template_name = 'market.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['products'] = Product.objects.all()
        context['categories'] = Category.objects.all()
        context['fav_ids'] = Favorite.objects.filter(user=self.request.user).values_list('product_id', flat=True)


        return context


class FlowViewList(CreateView):
    form_class = FlowForm
    template_name = 'market.html'
    success_url = reverse_lazy('market')

    def form_valid(self, form):
        flow = form.save(commit=False)
        flow.user = self.request.user
        flow.product_id = self.kwargs.get('id')
        flow.save()
        messages.success(self.request, f"Muffaqiyatli qo'shildi | ID: {flow.product_id}")
        return super().form_valid(form)

    def get_initial(self):
        initial = super().get_initial()
        initial['product'] = self.kwargs.get('id')
        return initial

    def form_invalid(self, form):
        for error in form.errors.values():
            messages.error(self.request, error)
        return redirect('market')



    # def form_valid(self, form):
    #     flow = form.save(commit=False)
    #     flow.user = self.request.user
    #     flow.product_id = self.kwargs.get('id')
    #     flow.save()
    #     messages.success(self.request, f"Muffaqiyatli qo'shildi | ID: {flow.product_id}")
    #     return super().form_valid(form)
    #
    # def get_form_kwargs(self):
    #     kwargs = super().get_form_kwargs()
    #     # pro_id = self.request.POST.get('id')
    #     pro_id = self.kwargs.get('id')
    #     kwargs['product'] = Product.objects.get(id=pro_id)
    #     return kwargs
    #
    # def form_invalid(self, form):
    #     for error in form.errors.values():
    #         messages.error(self.request, error)
    #     # return super().form_invalid(form)
    #     return redirect('market')


class StatsListView(ListView):
    queryset = Product.objects.all()
    template_name = 'statistika.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user
        today = timezone.now().date()
        orders = Order.objects.filter(flow__user=user)
        new = timezone.now() - timedelta(days=3)

        context['flows'] = Flow.objects.filter(user=user)
        context['visits'] = Flow.objects.filter(user=user).aggregate(total=Sum('visits'))['total']

        context['today'] = orders.filter(status=Order.StatusType.DELIVERING, delivery_date=today).count()
        context['after'] = orders.filter(status=Order.StatusType.DELIVERING, delivery_date__gt=today).count()
        context['new'] = Flow.objects.filter(created_at__gte=new).count()

        context['packing'] = orders.filter(status=Order.StatusType.PACKING).count()
        context['delivering'] = orders.filter(status=Order.StatusType.DELIVERING).count()
        context['delivered'] = orders.filter(status=Order.StatusType.DELIVERED).count()
        context['postponed'] = orders.filter(status=Order.StatusType.POSTPONED).count()
        context['returned'] = orders.filter(status=Order.StatusType.RETURNED).count()
        context['cancelled'] = orders.filter(status=Order.StatusType.CANCELLED).count()
        context['hold'] = orders.filter(status=Order.StatusType.HOLD).count()
        context['archive'] = orders.filter(status=Order.StatusType.ARCHIVE).count()

        context['products'] = Product.objects.filter(flows__user=user).distinct().annotate(
            visits=Sum('flows__visits', filter=Q(flows__user=user)),

            packing=Count('flows__orders', filter=Q(flows__user=user, flows__orders__status=Order.StatusType.PACKING)),
            delivering=Count('flows__orders',
                             filter=Q(flows__user=user, flows__orders__status=Order.StatusType.DELIVERING)),
            delivered=Count('flows__orders',
                            filter=Q(flows__user=user, flows__orders__status=Order.StatusType.DELIVERED)),
            postponed=Count('flows__orders',
                            filter=Q(flows__user=user, flows__orders__status=Order.StatusType.POSTPONED)),
            returned=Count('flows__orders',
                           filter=Q(flows__user=user, flows__orders__status=Order.StatusType.RETURNED)),
            cancelled=Count('flows__orders',
                            filter=Q(flows__user=user, flows__orders__status=Order.StatusType.CANCELLED)),
            hold=Count('flows__orders', filter=Q(flows__user=user, flows__orders__status=Order.StatusType.HOLD)),
            archive=Count('flows__orders', filter=Q(flows__user=user, flows__orders__status=Order.StatusType.ARCHIVE)),

            today=Count('flows__orders', filter=Q(
                flows__user=user,
                flows__orders__status=Order.StatusType.DELIVERING,
                flows__orders__delivery_date=today
            )),
            after=Count('flows__orders', filter=Q(
                flows__user=user,
                flows__orders__status=Order.StatusType.DELIVERING,
                flows__orders__delivery_date__gt=today
            )),
        )

        return context


class SettingsListView(ListView):
    queryset = User.objects.all()
    template_name = 'Sozlamalar.html'


class ProfileUpdateView(UpdateView):
    model=  User
    form_class = ProfileForm
    template_name = 'Sozlamalar.html'
    success_url = reverse_lazy('accaunt')
    pk_url_kwarg = "pk"


    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        context['user'] = User.objects.get(pk=self.request.user.id)
        return context


class CompetitionListView(ListView):
    queryset = User.objects.all()
    template_name = 'Konkurs.html'

    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)

        context['users'] = User.objects.all().annotate(
            sales=Count('flows__orders', filter=Q(flows__orders__status=Order.StatusType.DELIVERED)))


        return context


class WishListView(ListView):
    queryset = Favorite.objects.all()
    template_name = 'wishlist.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['favorites'] = Favorite.objects.filter(user=self.request.user).order_by('-created_at')
        context['categories'] = Category.objects.all()

        return context


class FavByCategoryView(ListView):
    queryset = Favorite.objects.all()
    template_name = 'wishlist.html'
    context_object_name = 'favorites'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        pk = self.request.GET.get('pk')

        context['favorites'] = Favorite.objects.filter(user=self.request.user).filter(product__category=pk)
        context['categories'] = Category.objects.all()

        return context


class FavCreateView(CreateView):
    queryset = Favorite.objects.all()
    template_name = 'market.html'
    form_class = FavModelForm
    success_url = reverse_lazy('market')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['products'] = Product.objects.all()
        context['categories'] = Category.objects.all()
        context['fav_ids'] = Favorite.objects.filter(user=self.request.user).values_list('product_id', flat=True)

        return context


class FavDelView(DeleteView):
    queryset = Favorite.objects.all()
    template_name = 'wishlist.html'
    context_object_name = 'favorite'
    success_url = reverse_lazy('wishlist')
    pk_url_kwarg = 'pk'




class ReferallView(ListView):
    queryset = User.objects.all()
    template_name = 'referal.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user']=User.objects.all()
        return context


class WithdrawListView(ListView):
    queryset = Product.objects.all()
    template_name = 'withdraw.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user

        context['transactions_count'] = Transaction.objects.filter(user=user).count()

        context['balance'] = user.balance

        context['transactions'] = Transaction.objects.filter(user=user).order_by('-created_at')

        return context
class TransactionCreateView(CreateView):
    queryset = Transaction.objects.all()
    template_name = 'withdraw.html'
    form_class = TransactionModelForm
    success_url = reverse_lazy('withdraw')

class FlowDeleteView(DeleteView):
    queryset = Flow.objects.all()
    template_name = 'urls.html'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('urls')

class UrlListView(ListView):
    queryset = Flow.objects.all()
    template_name = 'urls.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['flows'] = Flow.objects.all()

        return context

class OrderDetailView(DetailView):
    queryset = Order.objects.all()
    template_name = 'order-change.html'
    pk_url_kwarg = 'pk'
    context_object_name = 'order'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        pk = self.kwargs.get(self.pk_url_kwarg)

        order = Order.objects.filter(id=pk).first()

        if order.product:
            context['total'] = order.quantity * order.product.price
        elif order.flow:
            context['total'] = order.quantity * order.flow.discount

        context['regions'] = Region.objects.all()

        return context


class OrderUpdateView(UpdateView):
    queryset = Order.objects.all()
    form_class = OrderModelForm
    template_name = 'order-change.html'
    success_url = reverse_lazy('operator-page')
    pk_url_kwarg = 'pk'
class OperatorListView(ListView):
    queryset = Order.objects.all()
    template_name = 'operator-page.html'
    context_object_name = 'orders'

    def get_queryset(self):
        queryset = Order.objects.all()

        status = self.request.GET.get('status')
        category_id = self.request.GET.get('category_id')
        region_id = self.request.GET.get('region_id')
        district_id = self.request.GET.get('district_id')

        if status:
            queryset = queryset.filter(status=status)

        if category_id:
            queryset = queryset.filter(flow__product__category_id=category_id)

        if region_id:
            queryset = queryset.filter(flow__user__city__region_id=region_id)

        if district_id:
            queryset = queryset.filter(flow__user__city_id=district_id)

        return queryset.order_by('-id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['regions'] = Region.objects.all()
        context['cities'] = City.objects.all()
        context['categories'] = Category.objects.all()

        return context

class OrderCreateView(CreateView):
    queryset = Order.objects.all()
    template_name = 'product_detail.html'
    form_class = OrderModelForm
    success_url = reverse_lazy('market')


def get_districts_by_region(request):
    region_id = request.GET.get('region_id')
    city = City.objects.filter(region_id=region_id).values('id', 'title')
    return JsonResponse(list(city), safe=False)


class ProductListView(ListView):
    queryset = Product.objects.all()
    template_name = 'home.html'
    context_object_name = 'products'

    def get_queryset(self):
        query = self.request.GET.get('q', '').strip()
        queryset = Product.objects.all()

        if query:
            if self.request.user.is_authenticated:
                History.objects.get_or_create(
                    user=self.request.user,
                    request=query
                )

            queryset = queryset.filter(
                Q(title__icontains=query) | Q(description__icontains=query)
            ).distinct()

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['search_query'] = self.request.GET.get('q', '').strip()
        context['categories'] = Category.objects.all()

        return context