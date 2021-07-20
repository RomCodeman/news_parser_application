from django.db import models


class Category(models.Model):
    class Meta:
        verbose_name_plural = "Categories"

    category_id = models.IntegerField(unique=True)
    seo_title = models.CharField(max_length=50)
    title_ru = models.CharField(max_length=50)
    title_ua = models.CharField(max_length=50)
    title_genitive_ru = models.CharField(max_length=50)
    title_genitive_ua = models.CharField(max_length=50)

    def __str__(self):
        """String for representing the Category objects."""
        return self.title_ua


class Partner(models.Model):
    class Meta:
        verbose_name_plural = "Partners"

    partner_id = models.IntegerField(unique=True)
    title = models.CharField(max_length=100)

    def __str__(self):
        """String for representing the Partner objects."""
        return self.title


class News(models.Model):
    class Meta:
        verbose_name_plural = "News"
        ordering = ["pk"]

    news_id = models.IntegerField(unique=True)
    category = models.ManyToManyField('Category', related_name='Categories')
    cluster = models.ForeignKey("News", on_delete=models.PROTECT, related_name="clusters", null=True, blank=True)
    original = models.ForeignKey("News", on_delete=models.PROTECT, related_name="originals", null=True, blank=True)
    seo_title = models.SlugField(max_length=150, null=True)
    title = models.CharField(max_length=250)
    description = models.TextField()
    date_created = models.DateTimeField()
    url = models.CharField(max_length=250)
    partner = models.ForeignKey(Partner, on_delete=models.PROTECT)

    def __str__(self):
        """String for representing the News objects."""
        return f"{self.pk}"
