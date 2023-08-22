# TODO: create admin and check models viability
import json

from completion.models import BlockCompletion
from django.contrib import admin
from django.contrib import messages
from django.contrib.admin.sites import NotRegistered
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from simple_history.admin import SimpleHistoryAdmin
from polymorphic.admin import PolymorphicParentModelAdmin

from lektorium_main.courses.models import Course, Tag, COK, Section, Topic, TeachingMaterial
from lektorium_main.profile.models import TeacherProfile, StudentProfile, EducationalInstitution, \
    StatusMessage
from lektorium_main.statistics.models import EducontStatisticsItem, Transaction, TransactionErrorMessage
from lektorium_main.tilda.models import TildaArticle


class LEKTAdminSite(admin.AdminSite):
    site_header = _('LEKT administration')
    app_label = "lektorium_main"


lekt_admin_site = LEKTAdminSite(name='lekt_admin')

User = get_user_model()

try:
    admin.site.unregister(User)
except NotRegistered:
    pass


@admin.register(User, site=lekt_admin_site)
class UserAdmin(BaseUserAdmin):
    save_on_top = True
    search_fields = ('email', 'username')

    def get_ordering(self, request):
        return ['-date_joined']


@admin.register(StudentProfile, site=lekt_admin_site)
class StudentProfileAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ('fullName', 'email', 'user', 'isActive', 'statusConfirmEmail')
    search_fields = ('fullName', 'email', 'user__email')
    autocomplete_fields = ["user", ]


@admin.register(TeacherProfile, site=lekt_admin_site)
class TeacherProfileAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ('fullName', 'email', 'user', 'isActive', 'statusConfirmEmail')
    search_fields = ('fullName', 'email', 'user__email',)
    autocomplete_fields = ["user", ]


@admin.register(EducationalInstitution, site=lekt_admin_site)
class EducationalInstitutionAdmin(admin.ModelAdmin):
    list_display = ('shortName',)


#
# @admin.register(EducationalInstitutions, site=lekt_admin_site)
# class EducationalInstitutionsAdmin(admin.ModelAdmin):
#     list_display = ('id', 'approvedStatus', 'isActual',)


@admin.register(StatusMessage, site=lekt_admin_site)
class StatusMessageAdmin(admin.ModelAdmin):
    list_display = ('status_type', 'message',)


@admin.register(Tag, site=lekt_admin_site)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)
    search_fields = ('name', 'parent__name')
    list_filter = (
        ('parent', admin.EmptyFieldListFilter),
    )

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
class CourseAdmin(admin.ModelAdmin):  # PolymorphicParentModelAdmin):
    list_display = ('courseName', 'externalId',)
    search_fields = ('courseName', 'externalId')
    # base_model = Course  # Optional, explicitly set here.
    # child_models = (ModelB, ModelC)
    # polymorphic_list = True


@admin.register(COK, site=lekt_admin_site)
class COKAdmin(admin.ModelAdmin):
    save_on_top = True
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
    save_on_top = True
    list_display = ('externalId', 'courseName')
    search_fields = ('externalId', 'courseName')
    autocomplete_fields = ['externalParent', ]
    exclude_fields = ['order', ]
    ordering = ['order']


@admin.register(Topic, site=lekt_admin_site)
class TopicAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ('externalId', 'courseName')
    autocomplete_fields = ('externalParent',)
    exclude_fields = ['order', ]
    ordering = ['order']


@admin.register(TeachingMaterial, site=lekt_admin_site)
class TeachingMaterialAdmin(admin.ModelAdmin):
    save_on_top = True
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
    list_filter = ('statisticType', 'status')
    readonly_fields = ('transaction',)


class TransactionErrorMessageInline(admin.TabularInline):
    model = TransactionErrorMessage


@admin.register(Transaction, site=lekt_admin_site)
class TransactionAdmin(SimpleHistoryAdmin):
    list_display = ('id', 'status', 'created', 'modified')
    history_list_display = ('status',)
    inlines = [TransactionErrorMessageInline, ]


@admin.register(BlockCompletion, site=lekt_admin_site)
class BlockCompletionAdmin(admin.ModelAdmin):
    list_display = ('user', 'block_key')


@admin.register(TildaArticle, site=lekt_admin_site)
class TildaArticleAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ('course_id', )
    search_fields = ('course_id', )
    
    def save_model(self, request, obj, form, change):
        # распаковка архива при импорте
        archive_changed = 'archive' in form.changed_data
        
        # запишет файл на диск
        super(TildaArticleAdmin, self).save_model(request, obj, form, change)

        if archive_changed and obj.archive:
            obj.import_archive()