# TODO: create admin and check models viability
import json

from completion.models import BlockCompletion
from django.contrib import admin
from django.contrib import messages
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from lektorium_main.courses.models import Course, Tag, COK, Section, Topic, TeachingMaterial
from lektorium_main.profile.models import TeacherProfile, StudentProfile, EducationalInstitution, \
    EducationalInstitutions, StatusMessage
from lektorium_main.statistics.models import EducontStatisticsItem


class LEKTAdminSite(admin.AdminSite):
    site_header = _('LEKT administration')


lekt_admin_site = LEKTAdminSite(name='lekt_admin')


@admin.register(StudentProfile, site=lekt_admin_site)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('fullName', 'email', 'user', 'isActive', 'statusConfirmEmail', )
    search_fields = ('user__email')
    autocomplete_fields = ["user", ]

@admin.register(TeacherProfile, site=lekt_admin_site)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ('fullName', 'email', 'user', 'isActive', 'statusConfirmEmail', )
    search_fields = ('user__email')
    autocomplete_fields = ["user", ]


@admin.register(EducationalInstitution, site=lekt_admin_site)
class EducationalInstitutionAdmin(admin.ModelAdmin):
    list_display = ('shortName',)


@admin.register(EducationalInstitutions, site=lekt_admin_site)
class EducationalInstitutionsAdmin(admin.ModelAdmin):
    list_display = ('id', 'approvedStatus', 'isActual',)


@admin.register(StatusMessage, site=lekt_admin_site)
class StatusMessageAdmin(admin.ModelAdmin):
    list_display = ('status_type', 'message',)


@admin.register(Tag, site=lekt_admin_site)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)
    search_fields = ('name', 'parent__name')
    list_filter = ('parent',)

    autocomplete_fields = ["parent", ]


@admin.action(description='POST course')
def upload(modeladmin, request, queryset):
    for course in queryset:
        response = course.educont_upload()
        messages.info(request, f"{response.status_code}: {response.text}")


@admin.action(description='DELETE course')
def delete(modeladmin, request, queryset):
    for course in queryset:
        response = course.educont_delete()
        messages.info(request, f"{response.status_code}: {response.text}")


@admin.action(description='create_educont_objects')
def create_educont_objects(modeladmin, request, queryset):
    for course in queryset:
        course.create_educont_objects()


@admin.register(Course, site=lekt_admin_site)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('courseName', 'externalId',)
    search_fields = ('courseName', 'externalId')


@admin.register(COK, site=lekt_admin_site)
class COKAdmin(admin.ModelAdmin):
    list_display = ('courseName', 'externalLink', 'courseDescription')
    autocomplete_fields = ('tags',)
    readonly_fields = ('id', 'courseTypeId', 'raw_course_outline_data', 'created', 'modified',)
    search_fields = ('courseName', 'course_id')
    actions = [upload, create_educont_objects]

    fieldsets = (
        (
            'Common fields',
            {
                'fields': (
                    'id',
                    'externalId',
                    'courseName',
                    'courseTypeId',
                ),
            }
        ),
        (
            'Course-specific fields',
            {
                'fields': (
                    'course_id',
                    'externalLink',
                    'courseDescription',
                    'tags',
                    'courseImageFile',
                    'grades'
                )
            }
        ),
        (
            'Debug Details',
            {
                'fields': (
                    'created', 'modified', 'raw_course_outline_data'
                ),
                'classes': ('collapse',),
            }
        ),
    )

    def raw_course_outline_data(self, _obj):
        try:
            outline_data_dict = _obj.get_course_outline_data_dict()
            outline_data_json = json.dumps(outline_data_dict, indent=2, sort_keys=True)
            return format_html("<pre>\n{}\n</pre>", outline_data_json)
        except:
            return format_html("<pre>\nNone\n</pre>")


@admin.register(Section, site=lekt_admin_site)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('externalId', 'courseName')
    search_fields = ('externalId', 'courseName')
    autocomplete_fields = ['externalParent', ]
    exclude_fields = ['order', ]
    ordering = ['order']


@admin.register(Topic, site=lekt_admin_site)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('externalId', 'courseName')
    autocomplete_fields = ('externalParent',)
    exclude_fields = ['order', ]
    ordering = ['order']


@admin.register(TeachingMaterial, site=lekt_admin_site)
class TeachingMaterialAdmin(admin.ModelAdmin):
    list_display = ('externalId', 'courseName', 'tags_display')
    autocomplete_fields = ('tags',)
    exclude_fields = ['order', ]
    ordering = ['order']

    def tags_display(self, obj):
        return ", ".join([
            tag.name for tag in obj.tags.all()
        ])

    tags_display.short_description = "Теги"


@admin.register(EducontStatisticsItem, site=lekt_admin_site)
class EducontStatisticsItemAdmin(admin.ModelAdmin):
    list_display = ('statisticType', 'externalId', 'status', 'profileId', 'createdAt')


@admin.register(BlockCompletion, site=lekt_admin_site)
class BlockCompletionAdmin(admin.ModelAdmin):
    list_display = ('user', 'block_key')
