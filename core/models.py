from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# 1. الموديل المخصص للمستخدمين
class User(AbstractUser):
    department = models.CharField(max_length=100, default='الرئيسية', verbose_name='القسم')
    last_activity = models.DateTimeField(null=True, blank=True, verbose_name='آخر نشاط')

    def __str__(self):
        return f"{self.username} ({self.department})"
    
    def is_online(self):
        if self.last_activity:
            return (timezone.now() - self.last_activity).seconds < 300
        return False

    # --- الدالة الجديدة لحل مشكلة القالب ---
    def get_unread_notifications_count(self):
        """دالة مساعدة لجلب عدد الإشعارات غير المقروءة للاستخدام في القوالب"""
        if hasattr(self, 'notifications'):
            return self.notifications.filter(is_read=False).count()
        return 0

# 2. موديل الوثائق (الملفات)
class Document(models.Model):
    PRIORITY_CHOICES = [
        ('normal', 'عادية'),
        ('urgent', 'عاجل'),
        ('immediate', 'فوري'),
    ]
    title = models.CharField(max_length=255, verbose_name='العنوان / رقم الكتاب') 
    file = models.FileField(upload_to='documents/%Y/%m/%d/', verbose_name='الملف')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_documents', verbose_name='المرسل')
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإرسال')
    shared_with = models.ManyToManyField(User, related_name='received_documents', blank=True, verbose_name='مشاركة مع')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='normal', verbose_name='الأولوية')
    
    def __str__(self):
        return self.title

# 3. موديل حالة القراءة
class ReadStatus(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='read_statuses')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ('document', 'user')

# 4. موديل الرسائل الداخلية
class InternalMessage(models.Model):
    PRIORITY_CHOICES = [
        ('normal', 'عادية'),
        ('urgent', 'عاجل'),
        ('immediate', 'فوري'),
    ]
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient_department = models.CharField(max_length=100, verbose_name="القسم المستلم")
    subject = models.CharField(max_length=200, verbose_name="الموضوع", null=True, blank=True)
    body = models.TextField(verbose_name="نص الرسالة")
    created_at = models.DateTimeField(auto_now_add=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='normal', verbose_name='الأولوية')

    def __str__(self):
        return f"من {self.sender.username} إلى {self.recipient_department}"

# 5. موديل الإشعارات
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    link = models.CharField(max_length=255, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']