from django.urls import include, path


urlpatterns = [
    path('v1/', include('blog.api.v1.urls'))
]
