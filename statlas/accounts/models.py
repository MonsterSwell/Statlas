from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.urlresolvers import reverse
from django.contrib.admin.models import LogEntry as BaseLogEntry
from django.contrib.admin.models import LogEntryManager, ADDITION, CHANGE, DELETION # Keep for importing in other files

from statmap.models import DataSet


class Profile(models.Model):
    user                      = models.OneToOneField(User, related_name="profile")
    
    def get_absolute_url(self):
        return reverse('accounts:profile', args=[self.user.twitter_profile.screen_name])

class LogEntry(BaseLogEntry):
    objects = LogEntryManager()
    
    
    action_labels = { ADDITION: 'created',
                      CHANGE: 'edited',
                      DELETION: 'deleted'}
    
    def get_action_display(self):
        return self.action_labels[self.action_flag]
    
@receiver(post_save, sender=User, dispatch_uid="user_created_add_profile")
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        try:
            instance.profile
        except Profile.DoesNotExist:
            instance.profile = Profile(user=instance)
            instance.profile.save()
  