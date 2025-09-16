from drf_spectacular.utils import OpenApiParameter


theme_schema = {
    "parameters": [
            OpenApiParameter(
                "title",
                type={"type": "string"},
                description="Filter by title (ex. ?title=something)"
            ),
            OpenApiParameter(
                "theme",
                type={"type": "list", "items": {"type": "number"}},
                description="Filter by theme ids (ex. ?theme=2,3)"
            ),
        ]
}