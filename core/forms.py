from django import forms
from .models import Document, User, InternalMessage

class DocumentForm(forms.ModelForm):
    """
    نموذج رفع الملفات (الكتب الرسمية)
    يتضمن حقل الأولوية واختيار الأقسام المستلمة
    """
    shared_with = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="مشاركة مع الأقسام",
        required=True
    )

    class Meta:
        model = Document
        fields = ['title', 'priority', 'file', 'shared_with']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'العنوان أو رقم المرجع'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        # استلام المستخدم الحالي لاستبعاده من قائمة المشاركة (لا يرسل الشخص لنفسه)
        user = kwargs.pop('user', None)
        super(DocumentForm, self).__init__(*args, **kwargs)
        if user:
            # استبعاد المستخدم الحالي من القائمة
            self.fields['shared_with'].queryset = User.objects.exclude(id=user.id)
            # تعريب عرض أسماء المستخدمين ليظهر القسم بدلاً من اسم المستخدم فقط إذا أردت
            self.fields['shared_with'].label_from_instance = lambda obj: f"{obj.department} ({obj.username})"

class InternalMessageForm(forms.ModelForm):
    """
    نموذج إرسال الرسائل الداخلية بين الأقسام
    """
    # قائمة الأقسام المتاحة - يمكن تخصيصها حسب هيكلية الشركة
    DEPARTMENTS = [
        ('الإدارة العامة', 'الإدارة العامة'),
        ('الموارد البشرية', 'الموارد البشرية'),
        ('المالية', 'المالية'),
        ('تقنية المعلومات', 'تقنية المعلومات'),
        ('الشؤون القانونية', 'الشؤون القانونية'),
        ('العمليات', 'العمليات'),
        ('التسويق', 'التسويق'),
    ]
    
    recipient_department = forms.ChoiceField(
        choices=DEPARTMENTS, 
        label="القسم المستلم", 
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = InternalMessage
        fields = ['recipient_department', 'priority', 'subject', 'body']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'موضوع الرسالة'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'اكتب نص الرسالة هنا...'}),
        }