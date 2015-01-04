from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib import admin

from annotator.models import Annotator

class AnnotatorChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = Annotator

class AnnotatorCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Annotator

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            Annotator.objects.get(username=username)
        except Annotator.DoesNotExist:
            return username
        raise forms.ValidationError(self.error_messages['duplicate_username'])

class AnnotatorAdmin(UserAdmin):
    form = AnnotatorChangeForm
    add_form = AnnotatorCreationForm
    fieldsets = UserAdmin.fieldsets + (
            (None, {'fields': ('is_task_mode',)}),
            )

# Register your models here.
admin.site.register(Annotator, AnnotatorAdmin)
