######################
# producer/api/urls.py
######################

from django.urls import path

from producer.api.views import (
    generator_list, generator_create, generator_update, generator_delete,
    string_create, string_update, string_delete,
    generator_type_list, orientation_list,
    storage_list, storage_create, storage_update, storage_delete, storage_detect,
)


urlpatterns = [
    path(
        "",
        generator_list,
        name="generator-list",
    ),
    path(
        "create/",
        generator_create,
        name="generator-create",
    ),
    path(
        "<uuid:generator_id>/",
        generator_update,
    ),
    path(
        "<uuid:generator_id>/delete/",
        generator_delete,
    ),
    path(
        "types/",
        generator_type_list,
        name="generator-types",
    ),
    path(
        "orientations/",
        orientation_list,
        name="orientations",
    ),
    path(
        "string/create/",
        string_create,
        name="string-create",
    ),
    path(
        "string/<uuid:string_id>/",
        string_update,
    ),
    path(
        "string/<uuid:string_id>/delete/",
        string_delete,
    ),
    # 🔋 Storage Systems
    path(
        "storage/",
        storage_list,
        name="storage-list",
    ),
    path(
        "storage/create/",
        storage_create,
        name="storage-create",
    ),
    path(
        "storage/detect/",
        storage_detect,
        name="storage-detect",
    ),
    path(
        "storage/<uuid:storage_id>/",
        storage_update,
        name="storage-update",
    ),
    path(
        "storage/<uuid:storage_id>/delete/",
        storage_delete,
        name="storage-delete",
    ),
]
