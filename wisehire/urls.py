"""
URL configuration for wisehire project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
# wisehire/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from django.shortcuts import redirect
from django.conf.urls.i18n import i18n_patterns


def redirect_to_login(request):
    return redirect('login')


urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    
    # Admin
    path('admin/', admin.site.urls),
    
    # Root redirect to login
    path('', redirect_to_login, name='home'),
    
    # Web authentication routes
    path('auth/', include('accounts.urls')),
    
    # API routes
    path('api/auth/', include('accounts.urls')),
    path('api/companies/', include('companies.urls')),
    path('api/jobs/', include('jobs.urls')),
    path('api/candidates/', include('candidates.urls')),
    path('api/flows/', include('flows.urls')),
    path('api/', include('reports.urls')),
    #
    path('rosetta/', include('rosetta.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


