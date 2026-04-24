from django.urls import path
from . import views

app_name = "community"

urlpatterns = [
    path("", views.asset_list, name="asset_list"),
    path("asset/<str:asset_id>/", views.board, name="board"),
    path("asset/<str:asset_id>/post/new/", views.post_create, name="post_create"),
    path("asset/<str:asset_id>/post/<int:post_id>/", views.post_detail, name="post_detail"),
    path("asset/<str:asset_id>/post/<int:post_id>/edit/", views.post_update, name="post_update"),
    path("asset/<str:asset_id>/post/<int:post_id>/delete/", views.post_delete, name="post_delete"),
    path("asset/<str:asset_id>/post/<int:post_id>/comments/create/", views.comment_create, name="comment_create"),
    path("asset/<str:asset_id>/post/<int:post_id>/comments/<int:comment_id>/delete/", views.comment_delete, name="comment_delete"),
    
    # 포트폴리오 비동기 API
    path("portfolio/<str:portfolio_id>/comment/", views.portfolio_comment, name="portfolio_comment"),
    path("portfolio/<str:portfolio_id>/comments/", views.get_portfolio_comments, name="get_portfolio_comments"),
]
