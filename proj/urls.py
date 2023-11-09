"""
URL configuration for proj project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path('turberes/', admin.site.urls),
    path('', include('lupanes.urls')),
    path('', include('lupanes.users.urls')),
    path('', include('pwa.urls')),
    path('', RedirectView.as_view(pattern_name='lupanes:dashboard', permanent=True), name='root_index'),
    path('report-issue/', RedirectView.as_view(url='https://forms.gle/E4taAb3Xva2rfbKR9', permanent=True),
         name='report-issue')
]
