from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy

from .models import Document, ReadStatus, InternalMessage, Notification
from .forms import DocumentForm, InternalMessageForm

User = get_user_model()

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('core:dashboard') 
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('core:login') 

class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'core/change_password.html'
    success_url = reverse_lazy('core:dashboard')

    def form_valid(self, form):
        messages.success(self.request, 'تم تغيير كلمة المرور بنجاح.')
        return super().form_valid(form)

@login_required(login_url='core:login')
def dashboard(request):
    user = request.user
    search_query = request.GET.get('q', '')

    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES, user=user)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.uploaded_by = user
            doc.save()
            form.save_m2m()
            
            # إنشاء إشعارات للمستلمين
            for recipient in doc.shared_with.all():
                Notification.objects.create(
                    user=recipient,
                    message=f"تلقيت ملفاً جديداً: {doc.title} من {user.department}",
                    link='/dashboard/'
                )
                ReadStatus.objects.create(document=doc, user=recipient)
            
            messages.success(request, 'تم رفع الملف ومشاركته بنجاح.')
            return redirect('core:dashboard')
    else:
        form = DocumentForm(user=user)

    received_docs = Document.objects.filter(shared_with=user)
    sent_docs = Document.objects.filter(uploaded_by=user)
    
    if search_query:
        received_docs = received_docs.filter(Q(title__icontains=search_query) | Q(uploaded_by__username__icontains=search_query))
        sent_docs = sent_docs.filter(Q(title__icontains=search_query))

    active_users = User.objects.exclude(id=user.id).order_by('-last_activity')
    
    for doc in received_docs:
        status = ReadStatus.objects.filter(document=doc, user=user).first()
        doc.is_read_by_user = status.is_read if status else False

    return render(request, 'core/dashboard.html', {
        'form': form,
        'received_docs': received_docs.order_by('-uploaded_at'),
        'sent_docs': sent_docs.order_by('-uploaded_at'),
        'active_users': active_users,
        'search_query': search_query
    })

@login_required(login_url='core:login')
def mark_read(request, doc_id):
    doc = get_object_or_404(Document, id=doc_id)
    status, created = ReadStatus.objects.get_or_create(document=doc, user=request.user)
    if not status.is_read:
        status.is_read = True
        status.read_at = timezone.now()
        status.save()
    return redirect('core:dashboard')

@login_required(login_url='core:login')
def archive_view(request):
    user = request.user
    sent_docs = Document.objects.filter(uploaded_by=user)
    received_docs = Document.objects.filter(shared_with=user)
    all_docs = (sent_docs | received_docs).distinct().order_by('-uploaded_at')

    filter_type = request.GET.get('type')
    if filter_type == 'sent':
        all_docs = sent_docs.order_by('-uploaded_at')
    elif filter_type == 'received':
        all_docs = received_docs.order_by('-uploaded_at')

    return render(request, 'core/archive.html', {
        'documents': all_docs,
        'filter_type': filter_type
    })

@login_required(login_url='core:login')
def internal_mail(request):
    user = request.user
    
    if request.method == 'POST':
        form = InternalMessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.sender = user
            msg.save()
            
            # إشعار للمستخدمين في القسم المستهدف
            recipients = User.objects.filter(department=msg.recipient_department)
            for rec in recipients:
                Notification.objects.create(
                    user=rec,
                    message=f"رسالة داخلية جديدة من {user.department}: {msg.subject}",
                    link='/mail/'
                )
                
            messages.success(request, 'تم إرسال الرسالة بنجاح.')
            return redirect('core:internal_mail')
    else:
        form = InternalMessageForm()

    received_messages = InternalMessage.objects.filter(recipient_department=user.department).order_by('-created_at')
    sent_messages = InternalMessage.objects.filter(sender=user).order_by('-created_at')

    return render(request, 'core/internal_mail.html', {
        'form': form,
        'received_messages': received_messages,
        'sent_messages': sent_messages
    })

# ميزة الإحصائيات (جديد)
@login_required(login_url='core:login')
def statistics_view(request):
    dept_stats = User.objects.values('department').annotate(
        total_sent=Count('uploaded_documents', distinct=True),
        total_received=Count('received_documents', distinct=True)
    )
    return render(request, 'core/statistics.html', {'dept_stats': dept_stats})

# مسار تصفير الإشعارات (جديد)
@login_required(login_url='core:login')
def mark_notifications_read(request):
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return redirect(request.META.get('HTTP_REFERER', 'core:dashboard'))