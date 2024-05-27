from django.urls import path
from . import views
urlpatterns = [
    path('', views.rooms),
    path('<int:room_id>/', views.room),
    path("<int:room_id>/movie/", views.movie),
    path('<int:movie_id>/seat/', views.get_seat),
    path('<int:movie_id>/create-seat/', views.seat),


]
