# Read only api views for dashboard 
'''
1. Asset Summary KPIs 
2. Assets by brand/model
4. warranty expiring soon 
5. SRs summary
6. SR by type
7. Pending SR
8. Employee summary 
9. Employee by status - active or exited
10. Employee asset mapping 
'''
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from assets.models import AssetsAssets, AssetsEmployee, AssetsServicerequest, AssetsAllocations
# 1. Asset Summary API 
class AssetSummaryView(APIView):
    def get(self, request):
        total = AssetsAssets.objects.count()
        in_store = AssetsAssets.objects.filter(current_status='in-store').count()
        allocated = AssetsAssets.objects.filter(current_status='Allocated').count()
        damaged = AssetsAssets.objects.filter(current_status='Damage').count()

        return Response({
            "total assets" : total, 
            "in_store assets" : in_store,
            "allocated assets" : allocated,
            "damaged assets" : damaged
            })

# 2. Assets by model
class AssetFilterByBrandView(APIView):
    def get(self, request):
        brand = request.query_params.get('brand')
        model = request.query_params.get('model')

        qs = AssetsAssets.objects.all()

        if brand:
            qs = qs.filter(brand=brand)
        if model:
            qs = qs.filter(model_name=model)

        return Response({
            "count": qs.count()
        })
# 3. Warranty expiring soon (1 - 2 months)
from datetime import timedelta
class WarrantyExpiringView(APIView):
    def get(self, request):
        days = int(request.query_params.get('days', 60))
        today = timezone.now().date()
        end_date = today + timedelta(days=days)

        assets = AssetsAssets.objects.filter(
            warranty_end__gte=today,
            warranty_end__lte=end_date
        ).values(
            'asset_id',
            'brand',
            'model_name',
            'warranty_end',
            'current_status'
        )

        return Response(list(assets))
    
# 4. SR Summary
class ServiceRequestSummaryView(APIView):
    def get(self, request):
        total_sr = AssetsServicerequest.objects.count()
        open_sr = AssetsServicerequest.objects.filter(status='OPEN').count()
        approved_sr = AssetsServicerequest.objects.filter(status='APPROVED').count()
        completed_sr = AssetsServicerequest.objects.filter(status='COMPLETED').count()
        rejected_sr = AssetsServicerequest.objects.filter(status='REJECTED').count()

        return Response({
            "Total SR" : total_sr,
            "Open SR" : open_sr,
            "Approved SR" : approved_sr,
            "Completed SR" : completed_sr,
            "Rejected SR" : rejected_sr
        })
    
# 5. SR by type
class ServiceRequestByTypeView(APIView):
    def get(self, request):
       new_joinee = AssetsServicerequest.objects.filter(sr_type='NEW').count()
       replacement = AssetsServicerequest.objects.filter(sr_type='REPLACEMENT').count()
       exit_sr = AssetsServicerequest.objects.filter(sr_type='EXIT').count()

       return Response({
            "New Joinee SRs" : new_joinee,
            "Replacement SRs" : replacement,
            "Exit SRs" : exit_sr
        })
    
# 6. Pending SRs
class PendingServiceRequestView(APIView):
    def get(self, request):
       pending = AssetsServicerequest.objects.filter(status='OPEN').count()

       return Response({
            "Pending SRs" : pending
        })
    
# 7. Employee Summary
class EmployeeSummaryView(APIView):
    def get(self, request):
       total_emp = AssetsEmployee.objects.count()

       return Response({
            "Total Employees" : total_emp
        })
    
# 8. Employee Status
class EmployeeStatusView(APIView):
    def get(self, request):
       active = AssetsEmployee.objects.filter(employee_status='ACTIVE').count()
       exited = AssetsEmployee.objects.filter(employee_status='EXITED').count()

       return Response({
            "Active Employees" : active,
            "Exited Employees" : exited
        })
    
# 9. Employee by location
from django.db.models import Count
class EmployeeLocationView(APIView):
    def get(self, request):
        data = (
            AssetsEmployee.objects
            .values('employee_location')
            .annotate(count=Count('id'))
        )
        return Response(list(data))
# 10. Employee - Asset Mapping
class EmployeeAssetMappingView(APIView):
    def get(self, request):
        employees = AssetsEmployee.objects.filter(employee_status='ACTIVE')

        data = []

        for emp in employees:
            allocation = (
                AssetsAllocations.objects
                .filter(employee=emp, status__in=['ALLOCATED', 'REPLACED'])
                .order_by('-allocated_date')
                .select_related('asset', 'service_request')
                .first()
            )

            if allocation:
                asset = allocation.asset
                asset_data = {
                    "asset_id": asset.asset_id,
                    "brand": asset.brand,
                    "model": asset.model_name,
                    "status": asset.current_status
                }
                sr_no = allocation.service_request.sr_no
            else:
                asset_data = None
                sr_no = None

            data.append({
                "employee_id": emp.employee_id,
                "employee_name": emp.employee_name,
                "employee_email": emp.employee_email,
                "location": emp.employee_location,
                "asset": asset_data,
                "service_request": sr_no
            })

        return Response(data)