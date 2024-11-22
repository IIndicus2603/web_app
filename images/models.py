from django.db import models
import json


class Image(models.Model):
    image = models.ImageField(upload_to='images/')
    description = models.CharField(max_length=255, blank=True)
    tags = models.TextField(blank=True, default="")  # Add this line to store tags

    def set_tags(self, tags_list):
        self.tags = json.dumps(tags_list)  # Convert list to JSON string

    def get_tags(self):
        return json.loads(self.tags) if self.tags else []

    def __str__(self):
        return self.description or 'No description'
    
