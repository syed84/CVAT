from collections import defaultdict

from django.db.models import Count
from rest_framework import serializers
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from cvat.apps.engine.models import (
    Label,
    LabeledImage,
    LabeledInterval,
    LabeledShape,
    LabeledTrack,
    Task,
)
from cvat.apps.engine.permissions import TaskPermission


class AnnotationCountFilterSerializer(serializers.Serializer):
    label_id = serializers.IntegerField(required=False, min_value=1)


class AnnotationCountSerializer(serializers.Serializer):
    task_id = serializers.IntegerField()
    group_by = serializers.CharField()
    counts = serializers.ListField(child=serializers.DictField())
    total = serializers.IntegerField()


class AnnotationCountsView(APIView):
    def get(self, request, task_id: int):
        filters = AnnotationCountFilterSerializer(data=request.query_params)
        filters.is_valid(raise_exception=True)

        task_queryset = TaskPermission.create_scope_list(request).filter(
            Task.objects.filter(pk=task_id)
        )
        if not task_queryset.exists():
            raise NotFound("Task not found")

        annotation_models = (
            LabeledImage,
            LabeledShape,
            LabeledTrack,
            LabeledInterval,
        )
        label_filter = filters.validated_data.get("label_id")
        counts_by_label = defaultdict(int)

        for annotation_model in annotation_models:
            queryset = annotation_model.objects.filter(job__segment__task_id=task_id)
            if label_filter is not None:
                queryset = queryset.filter(label_id=label_filter)

            rows = queryset.values("label_id").annotate(count=Count("id"))
            for row in rows:
                counts_by_label[row["label_id"]] += row["count"]

        labels = Label.objects.filter(
            id__in=counts_by_label,
            **({"id": label_filter} if label_filter is not None else {}),
        ).values("id", "name")
        label_names = {label["id"]: label["name"] for label in labels}
        counts = [
            {
                "label_id": label_id,
                "label_name": label_names[label_id],
                "count": count,
            }
            for label_id, count in counts_by_label.items()
            if label_id in label_names
        ]
        counts.sort(key=lambda item: (-item["count"], item["label_name"], item["label_id"]))

        response = {
            "task_id": task_id,
            "group_by": "label",
            "counts": counts,
            "total": sum(item["count"] for item in counts),
        }
        return Response(AnnotationCountSerializer(response).data)
