from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Document, ReadStatus 

# 1. تخصيص واجهة المستخدم
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'department', 'is_staff', 'last_activity')
    search_fields = ('username', 'email', 'department')
    fieldsets = UserAdmin.fieldsets + (
        ('معلومات إضافية', {'fields': ('department',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('معلومات إضافية', {'fields': ('department',)}),
    )

# 2. تخصيص واجهة الوثائق
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_by', 'uploaded_at')
    list_filter = ('uploaded_by__department', 'uploaded_at')
    search_fields = ('title', 'uploaded_by__username')
    filter_horizontal = ('shared_with',)

# 3. تخصيص واجهة حالة القراءة
class ReadStatusAdmin(admin.ModelAdmin):
    list_display = ('document', 'user', 'is_read', 'read_at')
    list_filter = ('is_read', 'user__department')

admin.site.register(User, CustomUserAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(ReadStatus, ReadStatusAdmin)
