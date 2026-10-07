from django.urls import path

from .views import AnnotationCountsStreamView, AnnotationCountsView

app_name = "test"

urlpatterns = [
    path(
        "tasks/<int:task_id>/annotation-counts",
        AnnotationCountsView.as_view(),
        name="annotation-counts",
    ),
    path(
        "tasks/<int:task_id>/annotation-counts/stream",
        AnnotationCountsStreamView.as_view(),
        name="annotation-counts-stream",
    ),
]
