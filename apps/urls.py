from django.urls import path

from apps.views import *

urlpatterns = [
    path('', HomeViewList.as_view(), name="home"),
    path('',ProductListView.as_view(), name="product"),
    path('admin_page', AdminViewList.as_view(), name="admin"),
    path('profile/wishlist', WishListView.as_view(), name="wishlist"),
    path('profile/wishlist/fav-del/<int:pk>', FavDelView.as_view(), name='fav-del'),
    path('profile/wishlist/sort-by', FavByCategoryView.as_view(), name='fav-by-ctg'),
    path('admin-page/market/add_fav', FavCreateView.as_view(), name='fav-create'),

    path('admin_page/accaunt', AdminAccountViewList.as_view(), name="accaunt"),

    # path('category', ProductListView.as_view(), name="category"),
    path('category', CategoryListView.as_view(), name="category"),
    path('category/<int:pk>', CategoryListView.as_view(), name="category-id"),
    path('register', RegisterViewList.as_view(), name='register'),
    path('login', LoginViewList.as_view(), name='login'),
    path('product/<int:pk>', ProductDetailView.as_view(), name='product_detail'),
    path('market/', MarketView.as_view(), name='market'),
    path('market/<int:id>', FlowViewList.as_view(), name='flow-create'),
    path('market/static', StatsListView.as_view(), name='stats'),
    path('settings', SettingsListView.as_view(), name='settings'),
    path('settings/update/<int:pk>', ProfileUpdateView.as_view(), name='settings-update'),
    path('competition/ ', CompetitionListView.as_view(), name='competition'),
    path('referral/ ', ReferallView.as_view(), name='referral'),
    path('withdraw/ ',  WithdrawListView.as_view(), name='withdraw'),
    path('transaction/ ', TransactionCreateView.as_view(), name='transaction'),
    path('urls/ ', UrlListView.as_view(), name='urls'),
    path('flow/delete/<int:pk>', FlowDeleteView.as_view(), name='flow-del'),
    path('admin-page/operator-page', OperatorListView.as_view(), name='operator-page'),
    path('admin-page/operator-page/order/<int:pk>', OrderDetailView.as_view(), name='order-detail'),
    path('admin-page/operator-page/order/update/<int:pk>', OrderUpdateView.as_view(), name='order-update'),
    path('admin-page/operator-page/order/create', OrderCreateView.as_view(), name='order-create'),

]
