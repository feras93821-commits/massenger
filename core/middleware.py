from django.utils import timezone
from .models import User

class ActiveUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # تحديث وقت آخر نشاط للمستخدم الحالي
            # نستخدم update_fields لتقليل الضغط على قاعدة البيانات
            request.user.last_activity = timezone.now()
            request.user.save(update_fields=['last_activity'])
        
        response = self.get_response(request)
        return response