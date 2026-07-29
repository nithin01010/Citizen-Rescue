from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User,
    ResidentProfile,
    GuardianProfile,
    VolunteerProfile,
    SecurityProfile,
    EmergencyContact,
    Block,
    Flat,
    Society,
)


class OptimizedAdminMixin:
    """
    Mixin to optimize admin database save operations.
    Saves only the fields that were actually modified in the admin change form.
    """
    def save_model(self, request, obj, form, change):
        if change:
            updated_fields = form.changed_data
            if updated_fields:
                model_fields = [f.name for f in obj._meta.get_fields()]
                fields_to_save = [f for f in updated_fields if f in model_fields]
                if fields_to_save:
                    obj.save(update_fields=fields_to_save)
        else:
            super().save_model(request, obj, form, change)


class ResidentProfileInline(admin.StackedInline):
    model = ResidentProfile
    can_delete = False
    verbose_name_plural = 'Resident Profile'


class GuardianProfileInline(admin.StackedInline):
    model = GuardianProfile
    can_delete = False
    verbose_name_plural = 'Guardian Profile'


class VolunteerProfileInline(admin.StackedInline):
    model = VolunteerProfile
    can_delete = False
    verbose_name_plural = 'Volunteer Profile'


class SecurityProfileInline(admin.StackedInline):
    model = SecurityProfile
    can_delete = False
    verbose_name_plural = 'Security Profile'


@admin.register(User)
class UserAdmin(OptimizedAdminMixin, BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Platform Details', {'fields': ('role', 'phone_number', 'age',
         'alternate_phone', 'address', 'is_verified')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Platform Details', {'fields': ('role', 'phone_number', 'age',
         'alternate_phone', 'address', 'is_verified')}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name',
                    'role', 'phone_number', 'is_verified', 'is_staff')
    list_filter = ('role', 'is_verified', 'is_staff',
                   'is_superuser', 'is_active')
    search_fields = ('username', 'first_name', 'last_name',
                     'email', 'phone_number')


@admin.register(ResidentProfile)
class ResidentProfileAdmin(OptimizedAdminMixin, admin.ModelAdmin):
    list_display = ('user', 'flat', 'blood_group', 'is_senior_citizen')
    list_filter = ('flat__block', 'is_senior_citizen', 'blood_group')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'flat__flat_number')


@admin.register(GuardianProfile)
class GuardianProfileAdmin(OptimizedAdminMixin, admin.ModelAdmin):
    list_display = ('user', 'occupation', 'is_available')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')


@admin.register(VolunteerProfile)
class VolunteerProfileAdmin(OptimizedAdminMixin, admin.ModelAdmin):
    list_display = ('user', 'skills', 'is_available', 'id_proof_type')
    search_fields = ('user__username', 'user__first_name', 'user__last_name',
                     'skills')


@admin.register(SecurityProfile)
class SecurityProfileAdmin(OptimizedAdminMixin, admin.ModelAdmin):
    list_display = ('user', 'badge_number', 'assigned_gate', 'on_duty',
                    'shift_timing')
    search_fields = ('user__username', 'user__first_name', 'user__last_name',
                     'badge_number')


@admin.register(EmergencyContact)
class EmergencyContactAdmin(OptimizedAdminMixin, admin.ModelAdmin):
    list_display = ('resident', 'guardian', 'name', 'phone_number', 'relationship', 'priority', 'is_verified')
    list_filter = ('priority', 'is_verified', 'relationship')
    search_fields = ('resident__username', 'resident__first_name', 'resident__last_name',
                     'name', 'phone_number')


@admin.register(Society)
class SocietyAdmin(OptimizedAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'address')
    search_fields = ('name',)


@admin.register(Block)
class BlockAdmin(OptimizedAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'society')
    list_filter = ('society',)
    search_fields = ('name', 'society__name')


@admin.register(Flat)
class FlatAdmin(OptimizedAdminMixin, admin.ModelAdmin):
    list_display = ('flat_number', 'block', 'get_society')
    list_filter = ('block__society', 'block')
    search_fields = ('flat_number', 'block__name', 'block__society__name')

    @admin.display(ordering='block__society', description='Society')
    def get_society(self, obj):
        return obj.block.society.name


