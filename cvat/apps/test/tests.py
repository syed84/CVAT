from unittest import mock

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from cvat.apps.engine.models import Job, Label, LabeledShape, Segment, Task
from cvat.apps.iam.models import User


class AnnotationCountsApiTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="analytics-user", password="password")
        self.task = Task.objects.create(name="analytics-task", owner=self.user)
        segment = Segment.objects.create(task=self.task, start_frame=0, stop_frame=0)
        job = Job.objects.create(segment=segment)
        self.person = Label.objects.create(task=self.task, name="person")
        self.car = Label.objects.create(task=self.task, name="car")
        for label in (self.person, self.person, self.car):
            LabeledShape.objects.create(
                job=job,
                label=label,
                frame=0,
                type="rectangle",
                points=[0, 0, 10, 10],
            )
        self.url = reverse("test:annotation-counts", args=[self.task.id])
        self.client.force_authenticate(self.user)

    @mock.patch("cvat.apps.test.views.TaskPermission.create_scope_view")
    def test_returns_counts_grouped_by_label(self, create_scope_view):
        create_scope_view.return_value.check_access.return_value.allow = True

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total"], 3)
        self.assertEqual(response.data["counts"], [
            {"label_id": self.person.id, "label_name": "person", "count": 2},
            {"label_id": self.car.id, "label_name": "car", "count": 1},
        ])

    @mock.patch("cvat.apps.test.views.TaskPermission.create_scope_view")
    def test_filters_by_label(self, create_scope_view):
        create_scope_view.return_value.check_access.return_value.allow = True

        response = self.client.get(f"{self.url}?label_id={self.car.id}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total"], 1)
        self.assertEqual(response.data["counts"], [
            {"label_id": self.car.id, "label_name": "car", "count": 1},
        ])

    @mock.patch("cvat.apps.test.views.TaskPermission.create_scope_view")
    def test_denies_user_without_task_access(self, create_scope_view):
        create_scope_view.return_value.check_access.return_value.allow = False

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @mock.patch("cvat.apps.test.views.TaskPermission.create_scope_view")
    def test_returns_empty_counts_for_task_without_annotations(self, create_scope_view):
        create_scope_view.return_value.check_access.return_value.allow = True
        LabeledShape.objects.all().delete()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["counts"], [])
        self.assertEqual(response.data["total"], 0)

    def test_requires_authentication(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
