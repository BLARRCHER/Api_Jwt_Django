from django.urls import path

from blog.api.v1 import views

urlpatterns = [
    path('articles/', views.ArticlesListApi.as_view()),
    path('articles/<uuid:uuid>/', views.ArticlesDetailApi.as_view()),
    path('articles/create/', views.ArticlesCreateApi.as_view()),
    path('articles/delete/<uuid:uuid>/', views.ArticlesDeleteApi.as_view()),
    path('articles/edit/<uuid:uuid>/', views.ArticlesEditApi.as_view()),
    path('login/', views.LoginApi.as_view()),
    path('register/', views.RegisterApi.as_view()),
    path('user/', views.UserApi.as_view()),
    path('refresh/', views.RefreshApi.as_view()),
    path('logout', views.LogoutApi.as_view())
]
