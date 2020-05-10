from django.db import models
from django.conf import settings
from django.utils import timezone


class User(models.Model):
    name = models.CharField(max_length=50)
    type = models.IntegerField() # 0 = guest, 1 ~ 10 = user level
    file_key = models.CharField(max_length=10, null=True) 
    valid_start = models.DateTimeField()
    valid_end = models.DateTimeField(null=True)
    desc = models.CharField(max_length=512, null=True)
    reg_date = models.DateTimeField(default=timezone.now)
    mod_date = models.DateTimeField(blank=True, null=True)

    class Meta:
	    indexes = [
		models.Index(fields=['file_key'], name='file_key_idx')
	    ]

    def __str__(self):
        return 'type({}) - {}'.format(self.type, self.name)

    
    def add_user(self, name, type=0, days=365):
        pass


class UrlFile(models.Model):
    file_type = models.CharField(max_length=10, default='full') # 'full' or 'part'
    file_key = models.CharField(max_length=50, default='0000') 
    file_ver = models.CharField(max_length=50, default='0.0.1') # 
    file_name = models.CharField(max_length=256)
    file_path = models.CharField(max_length=512)
    desc = models.TextField()
    reg_date = models.DateTimeField(
            default=timezone.now)

    class Meta:
	    indexes = [
		models.Index(fields=['reg_date'], name='reg_date_idx')
	    ]

    def __str__(self):
        return '{} - {}'.format(self.file_name, self.file_path)
    

class CheckPoint(models.Model):
    file_type = models.CharField(max_length=10, default='full') # 'full' or 'part'
    file_ver = models.CharField(max_length=50, default='0.0.1') 
    start_idx = models.IntegerField()
    end_idx = models.IntegerField()
    salt_key = models.CharField(max_length=20, default='dalbit-x')
    affected_rows = models.IntegerField(default=0)
    file_path = models.CharField(max_length=512)
    reg_date = models.DateTimeField(default=timezone.now)
    
    class Meta:
	    indexes = [
		models.Index(fields=['reg_date'], name='reg_date_idx')
	    ]
    def __str__(self):
        return '[{}] {}.{} | {} rows(index {}~{}) | {} - {}'.format(str(self.reg_date)[:19], self.file_type, self.file_ver,
                self.affected_rows, self.start_idx, self.end_idx, self.file_path, self.salt_key)
