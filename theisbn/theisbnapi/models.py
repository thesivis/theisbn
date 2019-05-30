from django.db import models

# Create your models here.

class ISBN(models.Model):
    class Meta:
        db_table = "isbn"

    isbn13 = models.CharField(max_length=255)
    isbn10 = models.CharField(max_length=255)
    authors = models.CharField(max_length=255)
    edition = models.CharField(max_length=255, null=True)
    binding = models.CharField(max_length=255, null=True)
    publisher = models.CharField(max_length=255, null=True)
    published = models.CharField(max_length=255, null=True)
    title = models.CharField(max_length=255)
    
    def __str__(self):
        return self.title