from django.db import models
from django.shortcuts import reverse

class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        permissions = [
            ('can_view_goldpage', 'Can View Goldpage')
        ]

    def __str__(self):
        return self.title
        
    def get_absolute_url(self):
        return reverse("blog:post_detail", kwargs={"pk": self.pk})
    