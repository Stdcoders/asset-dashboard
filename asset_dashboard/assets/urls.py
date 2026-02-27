from django.urls import path
from assets.views import (
    AssetListView,
    InStoreAssetListView,
    AssetDetailView,
    CreateAssetView, 
    UpdateAssetView, 
    FilterAssetByBrand,
    ServiceRequestCreateView, 
    ServiceRequestDetailView, 
    ServiceRequestFilterTypeView, 
    ServiceRequestFilterStatusView,
    ServiceRequestListView, 
    ServiceRequestApproveView,
    ServiceRequestRejectView, 
    EmployeeListView, 
    EmployeeCreateView, 
    EmployeeDeactivateView, 
    EmployeeUpdateView
)
from assets.dashboard import (
    AssetSummaryView,
    AssetFilterByBrandView,
    WarrantyExpiringView,
    ServiceRequestSummaryView,
    ServiceRequestByTypeView,
    PendingServiceRequestView,
    EmployeeSummaryView,
    EmployeeStatusView,
    EmployeeLocationView,
    EmployeeAssetMappingView
)


urlpatterns = [
    # ---------------- ASSETS ----------------
    path('assets/', AssetListView.as_view()),
    path('assets/in-store/', InStoreAssetListView.as_view()),
    path('assets/filter/', FilterAssetByBrand.as_view()),
    path('assets/create/', CreateAssetView.as_view()),
    path('assets/<int:asset_id>/', AssetDetailView.as_view()),
    path('assets/<int:asset_id>/update/', UpdateAssetView.as_view()),

    # ---------------- SERVICE REQUESTS ----------------
    path('sr/', ServiceRequestListView.as_view()),
    path('sr/create/', ServiceRequestCreateView.as_view()),   # POST=create, GET=list
    path('sr-filter/type/', ServiceRequestFilterTypeView.as_view()),
    path('sr-filter/status/', ServiceRequestFilterStatusView.as_view()),
    path('sr/<str:sr_no>/', ServiceRequestDetailView.as_view()),
    path('sr/<str:sr_no>/approve/', ServiceRequestApproveView.as_view()),
    path('sr/<str:sr_no>/reject/', ServiceRequestRejectView.as_view()),

    # ----------------- EMPLOYEE REQUESTS -----------s----
    path('emp/', EmployeeListView.as_view()),
    path('emp/create', EmployeeCreateView.as_view()),
    path('emp/<int:employee_id>', EmployeeDeactivateView.as_view()),
    path('emp/deactivate/<int:employee_id>', EmployeeDeactivateView.as_view()),
    path('emp/update/<int:employee_id>', EmployeeUpdateView.as_view()),

    # -----------------------READ - ONLY REQUEST APIS --------------------
    path('dashboard/assets/summary/', AssetSummaryView.as_view()),
    path('dashboard/assets/filter/', AssetFilterByBrandView.as_view()),
    path('dashboard/assets/warranty-expiring/', WarrantyExpiringView.as_view()),
    path('dashboard/sr/summary/', ServiceRequestSummaryView.as_view()),
    path('dashboard/sr/by-type/', ServiceRequestByTypeView.as_view()),
    path('dashboard/sr/pending/', PendingServiceRequestView.as_view()),
    path('dashboard/employees/summary/', EmployeeSummaryView.as_view()),
    path('dashboard/employees/status/', EmployeeStatusView.as_view()),
    path('dashboard/employees/location/', EmployeeLocationView.as_view()),
    path('dashboard/employees/asset-mapping/', EmployeeAssetMappingView.as_view()),
]

