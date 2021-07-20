from parser_app.models import Category

from loggers_my.logger_common import logger_ukrnet


def cycling_categories(category_pks: list[int]):
    """
    A generator that, returns category instances from ``django.db.models.Category``, depending on the value of
    the PK's.

    :param category_pks: The list of integers with a Primary Keys of categories and may contain single PK or a sequence.
    :type category_pks: list of int or None

    :return: instance or instances of news category
    :rtype: django.db.models.Category.objects
    """
    categories = Category.objects.all()
    if 0 not in category_pks:
        categories = categories.filter(pk__in=category_pks)
    return categories


def add_categories_to_db(meta_categories_list: list[Category]):

    for category in meta_categories_list:
        category: Category
        try:
            category.save()

            logger_ukrnet.info(f'Category PK: {category.pk}. Category Title: \"{category.title_ua}\". | <<CREATED>>')
            logger_ukrnet.debug(f'Category PK: {category.pk}. Category Title: \"{category.title_ua}\". | <<CREATED>>')
        except:
            cat = Category.objects.get(category_id=category.category_id)
            cat.category_id = category.category_id
            cat.seo_title = category.seo_title
            cat.title_ru = category.title_ru
            cat.title_ua = category.title_ua
            cat.title_genitive_ru = category.title_genitive_ru
            cat.title_genitive_ua = category.title_genitive_ua
            cat.save()

            logger_ukrnet.info(f'Category PK: {cat.pk}. Category Title: \"{cat.title_ua}\". | <<UPDATED>>')
            logger_ukrnet.debug(f'Category PK: {cat.pk}. Category Title: \"{cat.title_ua}\". | <<UPDATED>>')

