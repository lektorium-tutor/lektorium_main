# TODO: create admin and check models viability
from django.contrib import admin
from lektorium_main.courses.models import Tag, COK, Section, Topic, EducationalCourse
from lektorium_main.profile.models import Profile, TeacherProfile, StudentProfile
from django.utils.translation import ugettext_lazy as _


class LEKTAdminSite(admin.AdminSite):
    site_header = _('LEKT administration')


lekt_admin_site = LEKTAdminSite(name='lekt_admin')


@admin.register(Tag, site=lekt_admin_site)
class Tag(admin.ModelAdmin):
    list_display = ('name', )
    search_fields = ('name', )
    # list_display = ('name',)
    # autocomplete_fields = ["parent", ]


@admin.register(COK, site=lekt_admin_site)
class COK(admin.ModelAdmin):
    list_display = ('courseTypeId', 'courseName')


@admin.register(Section, site=lekt_admin_site)
class Section(admin.ModelAdmin):
    list_display = ('externalId', 'courseTypeId', 'courseName')
    # autocomplete_fields = ["externalParent", ]


@admin.register(Topic, site=lekt_admin_site)
class Topic(admin.ModelAdmin):
    list_display = ('externalId', 'courseTypeId', 'courseName')


@admin.register(EducationalCourse, site=lekt_admin_site)
class Topic(admin.ModelAdmin):
    list_display = ('externalId', 'courseTypeId', 'courseName')


@admin.register(Profile, site=lekt_admin_site)
class Topic(admin.ModelAdmin):
    list_display = ('name', )
