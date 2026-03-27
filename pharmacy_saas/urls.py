from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from dashboard.views import landing_page

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', landing_page, name='landing_page'),
    path('dashboard/', include('dashboard.urls')),
    path('accounts/', include('accounts.urls')),
    path('drugs/', include('drugs.urls')),
    path('sales/', include('sales.urls')),
    path('purchases/', include('purchases.urls')),
    path('reports/', include('reports.urls')),
    path('subscriptions/', include('subscriptions.urls')),
    path('superadmin/', include('superadmin_panel.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)