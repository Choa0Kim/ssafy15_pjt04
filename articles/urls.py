from django.urls import path
from . import views

app_name = 'articles'
urlpatterns = [
    path('', views.index, name='index'),
    path('portfolio/', views.portfolio, name='portfolio'),
    path('portfolio/<str:portfolio_id>/comment/', views.portfolio_comment, name='portfolio_comment'),
    path('portfolio/<str:portfolio_id>/comments/', views.get_portfolio_comments, name='get_portfolio_comments'),
    path('asset/<str:asset_id>/', views.asset_board, name='asset_board'),
    path('asset/<str:asset_id>/create/', views.post_create, name='post_create'),
    path('post/<int:post_pk>/', views.post_detail, name='post_detail'),
    path('post/<int:post_pk>/update/', views.post_update, name='post_update'),
    path('post/<int:post_pk>/delete/', views.post_delete, name='post_delete'),
]
