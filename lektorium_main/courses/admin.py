# TODO: create admin and check models viability
from django.contrib import admin

from lektorium_main.courses.models import Tag, COK, Section, Topic, EducationalCourse


@admin.register(Tag)
class Tag(admin.ModelAdmin):
    list_display = ('name',)
    autocomplete_fields = ["parent", ]


@admin.register(COK)
class COK(admin.ModelAdmin):
    list_display = ('courseTypeId', 'courseName')


@admin.register(Section)
class Section(admin.ModelAdmin):
    list_display = ('externalId', 'courseTypeId', 'courseName')
    autocomplete_fields = ["externalParent", ]


@admin.register(Topic)
class Topic(admin.ModelAdmin):
    list_display = ('externalId', 'courseTypeId', 'courseName')


@admin.register(EducationalCourse)
class Topic(admin.ModelAdmin):
    list_display = ('externalId', 'courseTypeId', 'courseName')
