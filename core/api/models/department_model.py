from django.db import models

class Department(models.Model):
    branch = models.ForeignKey('Branch', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return f"{self.name} - {self.branch.name}"