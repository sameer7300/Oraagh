from django.contrib import admin
from .models import Lease, TeamMember, LeaseMedia, LeaseTeamMember
from django.db import models
from django.forms import TextInput, Widget
from django.utils.safestring import mark_safe

class TeamMemberInline(admin.TabularInline):
    model = LeaseTeamMember
    extra = 1

class LeaseMediaInline(admin.TabularInline):
    model = LeaseMedia
    extra = 1

class MapWidget(Widget):
    template_name = 'portfolio/admin/map_widget.html'

    def render(self, name, value, attrs=None, renderer=None):
        context = self.get_context(name, value, attrs)
        return self._render(self.template_name, context, renderer)

@admin.register(Lease)
class LeaseAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'size', 'location', 'mineral_type', 'operational_status', 'start_date', 'end_date', 'lease_term')
    list_filter = ('operational_status', 'start_date', 'end_date', 'mineral_type')
    search_fields = ('name', 'location', 'mineral_type')
    inlines = [TeamMemberInline, LeaseMediaInline]
    readonly_fields = ('id',)
    formfield_overrides = {
        models.DateField: {'widget': admin.widgets.AdminDateWidget},
    }

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'location':
            kwargs['widget'] = MapWidget()
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    def get_queryset(self, request):
        return super().get_queryset(request)

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    @admin.display(description="Lease Term")
    def lease_term(self, obj):
        return f"{obj.start_date} - {obj.end_date}"

    class Media:
        js = (
            'https://unpkg.com/leaflet@1.7.1/dist/leaflet.js',
            'portfolio/js/map_widget.js',
        )
        css = {
            'all': ('https://unpkg.com/leaflet@1.7.1/dist/leaflet.css',)
        }



@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'email', 'phone', 'created_at', 'updated_at')
    list_filter = ('position', 'created_at', 'updated_at')
    search_fields = ('name', 'position', 'bio', 'email', 'phone')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(LeaseMedia)
class LeaseMediaAdmin(admin.ModelAdmin):
    list_display = ('lease', 'is_video', 'caption')
    search_fields = ('lease__name', 'caption')
