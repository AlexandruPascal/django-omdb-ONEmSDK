from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path(
        'search_wizard/', views.SearchWizardView.as_view(),
        name='search_wizard'
    ),
    path(
        'movie/detail/<str:id>/', views.MovieDetailView.as_view(),
        name='movie_detail'
    ),
    path(
        'history/', views.HistoryView.as_view(),
        name='history'
    )
]
