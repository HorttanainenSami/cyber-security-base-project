from django.db import models

class Todo(models.Model):
    id = models.AutoField(primary_key=True)
    todo = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published")
    owner = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    def __str__(self):
        return self.todo
