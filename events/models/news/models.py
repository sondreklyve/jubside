from django.db import models
from django.utils.text import slugify


class TextContent(models.Model):
    """
    Some common fields for things that are possible to add to the front page.
    """
    headline = models.CharField(
        verbose_name="tittel",
        max_length=100,
        blank=True)
    lead_paragraph = models.TextField(
        verbose_name="ingress",
        blank=True,
        help_text="Vises på forsiden og i artikkelen")
    body = models.TextField(
        verbose_name="brødtekst",
        blank=True,
        help_text=(
            "Vises kun i artikkelen. "
            "Man kan her bruke <a href=\"http://en.wikipedia.org/wiki/Markdown\" target=\"_blank\">"
            "markdown</a> for å formatere teksten."))

    slug = models.SlugField(null=True, blank=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.headline)
        return super().save(*args, **kwargs)
