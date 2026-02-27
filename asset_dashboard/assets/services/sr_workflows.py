from django.utils import timezone
from rest_framework.exceptions import ValidationError
from assets.models import AssetsAllocations


def process_new_asset(sr):
    asset = sr.replacement_asset

    if not asset:
        raise ValidationError("Asset is required")

    if asset.current_status != 'in-store':
        raise ValidationError("Asset not available")

    asset.current_status = 'allocated'
    asset.save()

    AssetsAllocations.objects.create(
        asset=asset,
        employee=sr.employee,
        service_request=sr,
        allocated_date=timezone.now().date(),
        status='ALLOCATED',
        remarks='New asset allocated'
    )


def process_replacement(sr):
    old_asset = sr.current_asset
    new_asset = sr.replacement_asset

    if not old_asset or not new_asset:
        raise ValidationError("Both old and new assets are required")

    if new_asset.current_status != 'in-store':
        raise ValidationError("Replacement asset not available")

    old_asset.current_status = 'in-store'
    old_asset.save()

    new_asset.current_status = 'allocated'
    new_asset.save()

    AssetsAllocations.objects.create(
        asset=new_asset,
        employee=sr.employee,
        service_request=sr,
        allocated_date=timezone.now().date(),
        status='REPLACED',
        remarks='Asset replaced'
    )


def process_exit(sr):
    asset = sr.current_asset
    employee = sr.employee

    if not asset:
        raise ValidationError("Asset required for exit")

    asset.current_status = 'in-store'
    asset.save()

    employee.employee_status = 'EXITED'
    employee.exit_date = timezone.now().date()
    employee.save()
