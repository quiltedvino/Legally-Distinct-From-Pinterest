from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

# Create your models here.


class Comment(models.Model):
    poster = models.ForeignKey('auth.User',
                               related_name='comments',
                               on_delete=models.CASCADE)
    content = models.TextField(blank=False)
    created = models.DateTimeField(auto_now_add=True)
    target_ct = models.ForeignKey(ContentType,
                                  blank=True, null=True, related_name="comment_target",
                                  on_delete=models.CASCADE)
    target_id = models.PositiveIntegerField(null=False, blank=False)
    target = GenericForeignKey('target_ct', 'target_id')

    class Meta:
        indexes = [
            models.Index(fields=['poster']),
        ]

        ordering = ['-created']

    def __str__(self):
        return f'{self.poster} said "{self.content}" about {self.target}'

    def get_absolute_url(self):
        return self.target.get_absolute_url()
