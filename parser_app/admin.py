from django.contrib import admin

from parser_app.models import Category, Partner, News


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('pk', 'category_id', 'seo_title', 'title_ru', 'title_ua')


class CategoryInLine(admin.TabularInline):
    model = News.category.through


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ('partner_id', 'title')


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):

    list_display = ('pk', 'news_id', 'partner', 'seo_title', 'title', 'cluster', 'original', 'date_created')
    list_filter = ('category', 'date_created')

    inlines = [
        CategoryInLine,
    ]

    fieldsets = (
        ('Common information about news item', {
            'fields': ('news_id', 'date_created', 'category', 'partner', 'title', 'cluster', 'original')
        }),
        ('Additional information about news item', {
            'fields': ('seo_title', 'description', 'url')
        }),
    )
