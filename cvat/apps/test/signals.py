from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from cvat.apps.engine.models import LabeledImage, LabeledInterval, LabeledShape, LabeledTrack

from .stream import publish


def _task_id(instance):
    try:
        return instance.job.segment.task_id
    except AttributeError:
        return None


@receiver(post_save, sender=LabeledImage)
@receiver(post_save, sender=LabeledInterval)
@receiver(post_save, sender=LabeledShape)
@receiver(post_save, sender=LabeledTrack)
def annotation_saved(sender, instance, **kwargs):
    task_id = _task_id(instance)
    if task_id is not None:
        publish(task_id, {"type": "annotations.changed"})


@receiver(post_delete, sender=LabeledImage)
@receiver(post_delete, sender=LabeledInterval)
@receiver(post_delete, sender=LabeledShape)
@receiver(post_delete, sender=LabeledTrack)
def annotation_deleted(sender, instance, **kwargs):
    task_id = _task_id(instance)
    if task_id is not None:
        publish(task_id, {"type": "annotations.changed"})
