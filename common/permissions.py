from rest_framework import permissions

class IsHRUserPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            hasattr(request.user, 'hr_company') and
            request.user.hr_company is not None
        )

class CustomerCompanyPermission(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
            
        if hasattr(obj, 'customer_company'):
            return request.user.has_customer_company_permission(obj.customer_company)
        
        if hasattr(obj, 'job_posting'):
            return request.user.has_customer_company_permission(obj.job_posting.customer_company)
        
        if hasattr(obj, 'candidate_flow'):
            return request.user.has_customer_company_permission(obj.candidate_flow.job_posting.customer_company)
        
        return False

class HRCompanyPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
            
        if hasattr(obj, 'hr_company'):
            return obj.hr_company == request.user.hr_company
        
        if hasattr(obj, 'created_by'):
            return obj.created_by.hr_company == request.user.hr_company
        
        return False

class CandidateAccessPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        
        user_authorized_companies = request.user.get_authorized_customer_companies()
        
        return obj.candidate_flows.filter(
            hr_company=request.user.hr_company,
            job_posting__customer_company__in=user_authorized_companies
        ).exists()