from rest_framework import serializers
from assets.models import AssetsAssets, AssetsAllocations, AssetsEmployee, AssetsServicerequest

class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetsAssets
        fields = ('asset_id', 
                  'brand', 
                  'model_name',
                  'working_status', 
                  'memory', 'operating_system',
                  'vendor', 'warranty_start', 
                  'warranty_end', 'span', 
                  'current_status')
class AllocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetsAllocations
        fields = ('allocation_id', 
                  'employee', 
                  'asset',
                  'service_request', 
                  'allocated_date', 'status',
                  'remarks')
class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetsEmployee
        fields = ('employee_id', 
                  'employee_name', 
                  'employee_email',
                  'employee_location', 
                  'employee_status', 'joining_date',
                  'exit_date')

class ServiceRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetsServicerequest
        fields = ('sr_no', 
                  'employee', 
                  'sr_type',
                  'status', 
                  'current_asset', 'replacement_asset',
                  'remarks')