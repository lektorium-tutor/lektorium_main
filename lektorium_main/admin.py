# TODO: create admin and check models viability
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from lektorium_main.courses.models import Tag, COK, Section, Topic, TagCategory
from lektorium_main.profile.models import TeacherProfile, StudentProfile, EducationalInstitution, \
    EducationalInstitutions, StatusMessage
from lektorium_main.statistics.models import LoggedIn, StudentStatisticsItem



class LEKTAdminSite(admin.AdminSite):
    site_header = _('LEKT administration')


lekt_admin_site = LEKTAdminSite(name='lekt_admin')


@admin.register(StudentProfile, site=lekt_admin_site)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(TeacherProfile, site=lekt_admin_site)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(EducationalInstitution, site=lekt_admin_site)
class EducationalInstitutionAdmin(admin.ModelAdmin):
    list_display = ('shortName',)


@admin.register(EducationalInstitutions, site=lekt_admin_site)
class EducationalInstitutionsAdmin(admin.ModelAdmin):
    list_display = ('id', 'approvedStatus', 'isActual',)


@admin.register(StatusMessage, site=lekt_admin_site)
class StatusMessageAdmin(admin.ModelAdmin):
    list_display = ('status_type', 'message',)


@admin.register(TagCategory, site=lekt_admin_site)
class TagCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Tag, site=lekt_admin_site)
class TagAdmin(admin.ModelAdmin):
    list_display = ('tag_id', 'name',)
    search_fields = ('name', 'category')
    # filter_vertical = ('category',)

    # autocomplete_fields = ["parent", ]

@admin.action(description='POST course')
def upload(modeladmin, request, queryset):
    for course in queryset:
        course.educont_upload()

@admin.register(COK, site=lekt_admin_site)
class COKAdmin(admin.ModelAdmin):
    list_display = ('courseTypeId', 'courseName')
    actions = [upload,]


@admin.register(Section, site=lekt_admin_site)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('externalId', 'courseTypeId', 'courseName')
    # autocomplete_fields = ["externalParent", ]


@admin.register(Topic, site=lekt_admin_site)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('externalId', 'courseTypeId', 'courseName')


@admin.register(LoggedIn, site=lekt_admin_site)
class LoggedInAdmin(admin.ModelAdmin):
    list_display = ('user', 'profile_id', 'created')
    readonly_fields = ('user', 'profile_id', 'created', 'modified')


@admin.register(StudentStatisticsItem, site=lekt_admin_site)
class StudentStatisticsItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'module_type', 'position', 'score', 'created')
    fields = (
        'user', 'student_module', 'module_type', 'position', 'score',
        'block_id', 'block_type', 'course_key',
        'created'
    )
    readonly_fields = ('created',)
