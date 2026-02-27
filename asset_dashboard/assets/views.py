from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from assets.models import AssetsAssets, AssetsEmployee, AssetsServicerequest, AssetsAllocations
from assets.serializers import AssetSerializer, AllocationSerializer,EmployeeSerializer, ServiceRequestSerializer
from assets.services.sr_workflows import (
    process_new_asset,
    process_replacement,
    process_exit
)
# Create your views here.

# Asset APIs 

# 1. All assets - /get
class AssetListView(APIView):
    def get(self, request):
        assets = AssetsAssets.objects.all()
        serializer = AssetSerializer(assets, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# 2. In-store assets for allocation and replacement - /get
class InStoreAssetListView(APIView):
    def get(self, request):
        assets = AssetsAssets.objects.filter(current_status='in-store')
        serializer = AssetSerializer(assets, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
# 3. Asset by ID - /get validation API
class AssetDetailView(APIView):
    def get(self, request, asset_id):
        try:
            asset = AssetsAssets.objects.get(asset_id = asset_id)
        except AssetsAssets.DoesNotExist:
            return Response(
                {'error': 'Asset not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = AssetSerializer(asset)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
# 4. Create new asset from Bill / invoice
class CreateAssetView(APIView):
    def post(self, request):
        serializer = AssetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 5. Delete any asset 
class DeleteAssetView(APIView):
    def delete(self, request, asset_id):
        try:
            asset = AssetsAssets.objects.get(asset_id = asset_id)
        except AssetsAssets.DoesNotExist:
            return Response({'error' : 'Asset not found'},status=404)
        asset.is_active = False
        asset.save()

# 6. Update any existing asset 
class UpdateAssetView(APIView):
     def put(self, request, asset_id):
        try:
            asset = AssetsAssets.objects.get(asset_id=asset_id)
        except AssetsAssets.DoesNotExist:
            return Response({'error': 'Asset not found'}, status=404)

        serializer = AssetSerializer(asset, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

# 7. Assets by brand and models 
class FilterAssetByBrand(APIView):
    def get(self, request):
        brand = request.GET.get('brand')
        model = request.GET.get('model')

        assets = AssetsAssets.objects.all()

        if brand:
            assets = assets.filter(brand__iexact=brand)
        if model:
            assets = assets.filter(model_name__icontains=model)

        serializer = AssetSerializer(assets, many=True)
        return Response(serializer.data)
     

# Service Requests APIs 
'''
Create SR
List SRs
Get SR
Approve SR
Reject SR
Filter by Type
Filter by Status
'''
# 1. Create a new service request
class ServiceRequestCreateView(APIView):
    def post(self, request):
        serializer = ServiceRequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 2. Get details of service request
class ServiceRequestDetailView(APIView):
    def get(self, request, sr_no):
        try:
            servicerequest = AssetsServicerequest(sr_no = sr_no)
        except AssetsServicerequest.DoesNotExist:
            return Response({'error' : 'Service Request not found'}, status=404)
        serializer = ServiceRequestSerializer(servicerequest)
        return Response(serializer.data, status=200)
    
# 3. Get all service requests
class ServiceRequestListView(APIView):
    def get(self, request):
        servicerequest = AssetsServicerequest.objects.all()
        serializer = ServiceRequestSerializer(servicerequest, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
# 4. Get service request by type - allocation, replacement, exit
class ServiceRequestFilterTypeView(APIView):
    def get(self, request):
        sr_type = request.GET.get('type')

        servicerequests = AssetsServicerequest.objects.all()

        if sr_type:
            servicerequests = servicerequests.filter(sr_type__iexact=sr_type)

        serializer = ServiceRequestSerializer(servicerequests, many=True)
        return Response(serializer.data)

# 5. Get service request by status - approved, rejected, pending
class ServiceRequestFilterStatusView(APIView):
    def get(self, request):
        sr_status = request.GET.get('status')

        servicerequests = AssetsServicerequest.objects.all()

        if sr_status:
            servicerequests = servicerequests.filter(status__iexact=sr_status)

        serializer = ServiceRequestSerializer(servicerequests, many=True)
        return Response(serializer.data)
    
# 6. Approve Service Requests

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError
class ServiceRequestApproveView(APIView):

    @transaction.atomic
    def post(self, request, sr_no):
        try:
            sr = AssetsServicerequest.objects.select_for_update().get(sr_no=sr_no)
        except AssetsServicerequest.DoesNotExist:
            return Response({'error': 'Service Request not found'}, status=404)

        # -------- Lifecycle checks --------
        if sr.status != 'OPEN':
            return Response(
                {'error': f'SR already {sr.status}'},
                status=400
            )

        # -------- Move to APPROVED --------
        sr.status = 'APPROVED'
        sr.save()

        try:
            if sr.sr_type == 'NEW':
                process_new_asset(sr)

            elif sr.sr_type == 'REPLACEMENT':
                process_replacement(sr)

            elif sr.sr_type == 'EXIT':
                process_exit(sr)

            else:
                raise ValidationError("Invalid SR type")

        except ValidationError as e:
            transaction.set_rollback(True)
            return Response({'error': str(e)}, status=400)

        # -------- Move to COMPLETED --------
        sr.status = 'COMPLETED'
        sr.save()

        return Response(
            {'message': f'Service Request {sr_no} approved and completed'},
            status=status.HTTP_200_OK
        )
# 7. Rejecting service request
class ServiceRequestRejectView(APIView):

    def post(self, request, sr_no):
        reason = request.data.get('reason')

        if not reason:
            return Response(
                {'error': 'Rejection reason is required'},
                status=400
            )

        try:
            sr = AssetsServicerequest.objects.get(sr_no=sr_no)
        except AssetsServicerequest.DoesNotExist:
            return Response({'error': 'Service Request not found'}, status=404)

        if sr.status != 'OPEN':
            return Response(
                {'error': f'SR already {sr.status}'},
                status=400
            )

        sr.status = 'REJECTED'
        sr.remarks = reason
        sr.save()

        return Response(
            {'message': f'Service Request {sr_no} rejected'},
            status=200
        )

'''Employee API Views'''
'''
✅ Create Employee
✅ List Employees
✅ Get Employee
✅ Update Employee
✅ Deactivate Employee
✅ Employee Assets
✅ Employee Service Requests
'''
# Employee APIs
# 1. Adding an employee to the list
class EmployeeCreateView(APIView):
    def post(self, request):
        serializer = EmployeeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 2. Removing an employee from the records
class EmployeeDeactivateView(APIView):
    def delete(self, request, employee_id):
        try:
            emp = AssetsEmployee.objects.get(employee_id = employee_id)
        except AssetsEmployee.DoesNotExist:
            return Response({'error' : 'Employee not found'},status=404)
        emp.employee_status = "INACTIVE"
        emp.save()
        return Response(status=200)

# 3. List all the employees
class EmployeeListView(APIView):
    def get(self, request):
        emp = AssetsEmployee.objects.all()
        serializer = EmployeeSerializer(emp, many=True)
        return Response(serializer.data, status=200)
    
# 4. List employee details
class EmployeeDetailView(APIView):
    def get(self, request, employee_id):
        try:
            emp = AssetsEmployee.objects.get(employee_id = employee_id)
        except AssetsEmployee.DoesNotExist:
            return Response(
                {'error': 'Employee not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = EmployeeSerializer(emp)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
# 5. Update employee details 
class EmployeeUpdateView(APIView):
    def patch(self, request, employee_id):
        try:
            emp = AssetsEmployee.objects.get(employee_id=employee_id)
        except AssetsEmployee.DoesNotExist:
            return Response({'error': 'Employee not found'}, status=404)

        serializer = EmployeeSerializer(emp, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)



        

