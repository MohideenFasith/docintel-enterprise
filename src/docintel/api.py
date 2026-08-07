from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request, Response, status

from .annotations import Annotation

from .errors import (
    DocumentNotFound,
    DuplicateDocument,
    InvalidDocument,
    PermissionDenied,
    RateLimitExceeded,
    WorkflowNotFound,
)
from .models import AnnotationIn, AnnotationPatch, DocumentIn, DocumentPatch, IngestionPolicy, SavedSearchIn, WorkflowRule
from .policies import PolicyNotFound
from .saved_searches import SavedSearchNotFound
from .security import ApiKeyAuthenticator, Principal, SlidingWindowRateLimiter
from .service import DocumentService


router = APIRouter()


def annotation_response(item: Annotation) -> dict[str, object]:
    """Serialize set-backed labels deterministically at the HTTP boundary."""
    return {
        "id": item.id,
        "document_id": item.document_id,
        "author": item.author,
        "body": item.body,
        "labels": sorted(item.labels),
        "created_at": item.created_at,
        "updated_at": item.updated_at,
    }


def service_from_request(request: Request) -> DocumentService:
    return request.app.state.service


def authenticator_from_request(request: Request) -> ApiKeyAuthenticator:
    return request.app.state.authenticator


def limiter_from_request(request: Request) -> SlidingWindowRateLimiter:
    return request.app.state.rate_limiter


def principal(
    request: Request,
    x_api_key: str | None = Header(default=None),
    auth: ApiKeyAuthenticator = Depends(authenticator_from_request),
) -> Principal:
    try:
        result = auth.authenticate(x_api_key)
        key = f"{result.name}:{request.client.host if request.client else 'local'}"
        limiter_from_request(request).check(key)
        return result
    except PermissionDenied as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(exc)) from exc
    except RateLimitExceeded as exc:
        raise HTTPException(
            status.HTTP_429_TOO_MANY_REQUESTS,
            "rate limit exceeded",
            headers={"Retry-After": str(exc)},
        ) from exc


@router.get("/health")
def health(request: Request) -> dict:
    return {"status": "ok", "environment": request.app.state.settings.app_env}


@router.get("/ready")
def ready(service: DocumentService = Depends(service_from_request)) -> dict:
    return {"status": "ready", **service.stats()}


@router.post("/documents", status_code=status.HTTP_201_CREATED)
def ingest(
    payload: DocumentIn,
    user: Principal = Depends(principal),
    service: DocumentService = Depends(service_from_request),
):
    try:
        return service.ingest(payload, actor=user.name)
    except DuplicateDocument as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, f"duplicate of {exc}") from exc
    except InvalidDocument as exc:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, str(exc)) from exc


@router.get("/documents")
def list_documents(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    source: str | None = None,
    tag: str | None = None,
    _: Principal = Depends(principal),
    service: DocumentService = Depends(service_from_request),
):
    return service.list(offset=offset, limit=limit, source=source, tag=tag)


@router.get("/documents/{document_id}")
def get_document(
    document_id: str,
    _: Principal = Depends(principal),
    service: DocumentService = Depends(service_from_request),
):
    try:
        return service.get(document_id)
    except DocumentNotFound as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "document not found") from exc


@router.patch("/documents/{document_id}")
def patch_document(
    document_id: str,
    payload: DocumentPatch,
    user: Principal = Depends(principal),
    service: DocumentService = Depends(service_from_request),
):
    try:
        return service.patch(document_id, payload, actor=user.name)
    except DocumentNotFound as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "document not found") from exc
    except DuplicateDocument as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, f"duplicate of {exc}") from exc
    except InvalidDocument as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc)) from exc


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: str,
    user: Principal = Depends(principal),
    service: DocumentService = Depends(service_from_request),
) -> Response:
    try:
        service.delete(document_id, actor=user.name)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except DocumentNotFound as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "document not found") from exc


@router.post("/documents/{document_id}/reindex")
def reindex_document(
    document_id: str,
    user: Principal = Depends(principal),
    service: DocumentService = Depends(service_from_request),
):
    try:
        return service.reindex(document_id, actor=user.name)
    except DocumentNotFound as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "document not found") from exc


@router.get("/search")
def search(
    q: str = Query(min_length=2, max_length=500),
    limit: int = Query(default=10, ge=1, le=100),
    tag: str | None = None,
    source: str | None = None,
    _: Principal = Depends(principal),
    service: DocumentService = Depends(service_from_request),
):
    return service.search(q, limit, tag=tag, source=source)


@router.get("/workflows")
def list_workflows(
    _: Principal = Depends(principal),
    service: DocumentService = Depends(service_from_request),
):
    return service.workflows.list()


@router.put("/workflows/{name}")
def put_workflow(
    name: str,
    payload: WorkflowRule,
    user: Principal = Depends(principal),
    service: DocumentService = Depends(service_from_request),
):
    if name != payload.name:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "path name must match payload name")
    try:
        ApiKeyAuthenticator.require(user, "admin")
        return service.upsert_workflow(payload, actor=user.name)
    except PermissionDenied as exc:
        raise HTTPException(status.HTTP_403_FORBIDDEN, str(exc)) from exc


@router.delete("/workflows/{name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workflow(
    name: str,
    user: Principal = Depends(principal),
    service: DocumentService = Depends(service_from_request),
) -> Response:
    try:
        ApiKeyAuthenticator.require(user, "admin")
        service.workflows.delete(name)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except PermissionDenied as exc:
        raise HTTPException(status.HTTP_403_FORBIDDEN, str(exc)) from exc
    except WorkflowNotFound as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "workflow not found") from exc


@router.get("/documents/{document_id}/route")
def route_document(
    document_id: str,
    _: Principal = Depends(principal),
    service: DocumentService = Depends(service_from_request),
):
    try:
        return service.route(document_id)
    except DocumentNotFound as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "document not found") from exc


@router.get("/admin/audit")
def audit_events(
    limit: int = Query(default=100, ge=1, le=1_000),
    actor: str | None = None,
    action: str | None = None,
    user: Principal = Depends(principal),
    service: DocumentService = Depends(service_from_request),
):
    try:
        ApiKeyAuthenticator.require(user, "admin")
    except PermissionDenied as exc:
        raise HTTPException(status.HTTP_403_FORBIDDEN, str(exc)) from exc
    return service.audit.list(limit=limit, actor=actor, action=action)


@router.post("/saved-searches", status_code=status.HTTP_201_CREATED)
def create_saved_search(
    payload: SavedSearchIn,
    user: Principal = Depends(principal),
    service: DocumentService = Depends(service_from_request),
):
    return service.create_saved_search(payload, actor=user.name)


@router.get("/saved-searches")
def list_saved_searches(
    user: Principal = Depends(principal),
    service: DocumentService = Depends(service_from_request),
):
    return service.list_saved_searches(actor=user.name)


@router.put("/saved-searches/{search_id}")
def replace_saved_search(
    search_id: str,
    payload: SavedSearchIn,
    user: Principal = Depends(principal),
    service: DocumentService = Depends(service_from_request),
):
    try:
        return service.replace_saved_search(search_id, payload, actor=user.name)
    except SavedSearchNotFound as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "saved search not found") from exc


@router.post("/saved-searches/{search_id}/run")
def run_saved_search(
    search_id: str,
    user: Principal = Depends(principal),
    service: DocumentService = Depends(service_from_request),
):
    try:
        return service.run_saved_search(search_id, actor=user.name)
    except SavedSearchNotFound as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "saved search not found") from exc


@router.delete("/saved-searches/{search_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_saved_search(
    search_id: str,
    user: Principal = Depends(principal),
    service: DocumentService = Depends(service_from_request),
) -> Response:
    try:
        service.delete_saved_search(search_id, actor=user.name)
    except SavedSearchNotFound as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "saved search not found") from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/ingestion-policies")
def list_ingestion_policies(
    user: Principal = Depends(principal),
    service: DocumentService = Depends(service_from_request),
):
    try:
        ApiKeyAuthenticator.require(user, "admin")
    except PermissionDenied as exc:
        raise HTTPException(status.HTTP_403_FORBIDDEN, str(exc)) from exc
    return service.policies.list()


@router.put("/ingestion-policies/{name}")
def put_ingestion_policy(
    name: str,
    payload: IngestionPolicy,
    user: Principal = Depends(principal),
    service: DocumentService = Depends(service_from_request),
):
    if name != payload.name:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "path name must match payload name")
    try:
        ApiKeyAuthenticator.require(user, "admin")
        return service.upsert_ingestion_policy(payload, actor=user.name)
    except PermissionDenied as exc:
        raise HTTPException(status.HTTP_403_FORBIDDEN, str(exc)) from exc


@router.post("/ingestion-policies/evaluate")
def evaluate_ingestion_policy(
    payload: DocumentIn,
    _: Principal = Depends(principal),
    service: DocumentService = Depends(service_from_request),
):
    return service.evaluate_ingestion_policy(payload)


@router.delete("/ingestion-policies/{name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ingestion_policy(
    name: str,
    user: Principal = Depends(principal),
    service: DocumentService = Depends(service_from_request),
) -> Response:
    try:
        ApiKeyAuthenticator.require(user, "admin")
        service.delete_ingestion_policy(name, actor=user.name)
    except PermissionDenied as exc:
        raise HTTPException(status.HTTP_403_FORBIDDEN, str(exc)) from exc
    except PolicyNotFound as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "ingestion policy not found") from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/admin/search-analytics")
def search_analytics(
    limit: int = Query(default=20, ge=1, le=500),
    zero_results_only: bool = False,
    user: Principal = Depends(principal),
    service: DocumentService = Depends(service_from_request),
):
    try:
        ApiKeyAuthenticator.require(user, "admin")
    except PermissionDenied as exc:
        raise HTTPException(status.HTTP_403_FORBIDDEN, str(exc)) from exc
    return service.search_analytics_snapshot(limit=limit, zero_results_only=zero_results_only)


@router.delete("/admin/search-analytics", status_code=status.HTTP_204_NO_CONTENT)
def reset_search_analytics(
    user: Principal = Depends(principal),
    service: DocumentService = Depends(service_from_request),
) -> Response:
    try:
        ApiKeyAuthenticator.require(user, "admin")
        service.reset_search_analytics(actor=user.name)
    except PermissionDenied as exc:
        raise HTTPException(status.HTTP_403_FORBIDDEN, str(exc)) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/collections", status_code=status.HTTP_201_CREATED)
def create_collection(
    name: str = Query(min_length=1, max_length=120),
    description: str = Query(default="", max_length=500),
    user: Principal = Depends(principal),
    service: DocumentService = Depends(service_from_request),
):
    try:
        return service.create_collection(name, description, actor=user.name)
    except ValueError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc


@router.get("/collections")
def list_collections(
    _: Principal = Depends(principal),
    service: DocumentService = Depends(service_from_request),
):
    return service.collections.list()


@router.get("/collections/{collection_id}")
def get_collection(
    collection_id: str,
    _: Principal = Depends(principal),
    service: DocumentService = Depends(service_from_request),
):
    try:
        return service.collections.get(collection_id)
    except KeyError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "collection not found") from exc


@router.put("/collections/{collection_id}/documents/{document_id}")
def add_collection_document(
    collection_id: str,
    document_id: str,
    user: Principal = Depends(principal),
    service: DocumentService = Depends(service_from_request),
):
    try:
        return service.add_document_to_collection(collection_id, document_id, actor=user.name)
    except DocumentNotFound as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "document not found") from exc
    except KeyError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "collection not found") from exc


@router.delete("/collections/{collection_id}/documents/{document_id}")
def remove_collection_document(
    collection_id: str,
    document_id: str,
    user: Principal = Depends(principal),
    service: DocumentService = Depends(service_from_request),
):
    try:
        return service.remove_document_from_collection(collection_id, document_id, actor=user.name)
    except KeyError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "collection not found") from exc


@router.delete("/collections/{collection_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_collection(
    collection_id: str,
    user: Principal = Depends(principal),
    service: DocumentService = Depends(service_from_request),
) -> Response:
    try:
        service.delete_collection(collection_id, actor=user.name)
    except KeyError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "collection not found") from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/documents/{document_id}/annotations", status_code=status.HTTP_201_CREATED)
def create_annotation(
    document_id: str,
    payload: AnnotationIn,
    user: Principal = Depends(principal),
    service: DocumentService = Depends(service_from_request),
):
    try:
        return annotation_response(service.create_annotation(document_id, payload.body, set(payload.labels), actor=user.name))
    except DocumentNotFound as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "document not found") from exc


@router.get("/documents/{document_id}/annotations")
def list_annotations(
    document_id: str,
    _: Principal = Depends(principal),
    service: DocumentService = Depends(service_from_request),
):
    try:
        service.get(document_id)
    except DocumentNotFound as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "document not found") from exc
    return [annotation_response(item) for item in service.annotations.list_for_document(document_id)]


@router.patch("/annotations/{annotation_id}")
def patch_annotation(
    annotation_id: str,
    payload: AnnotationPatch,
    user: Principal = Depends(principal),
    service: DocumentService = Depends(service_from_request),
):
    try:
        fields = payload.model_fields_set
        return annotation_response(
            service.update_annotation(
                annotation_id,
                body=payload.body if "body" in fields else None,
                labels=set(payload.labels or []) if "labels" in fields else None,
                actor=user.name,
            )
        )
    except KeyError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "annotation not found") from exc
    except ValueError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc)) from exc


@router.delete("/annotations/{annotation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_annotation(
    annotation_id: str,
    user: Principal = Depends(principal),
    service: DocumentService = Depends(service_from_request),
) -> Response:
    try:
        service.delete_annotation(annotation_id, actor=user.name)
    except KeyError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "annotation not found") from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/documents/{document_id}/versions")
def list_document_versions(
    document_id: str,
    _: Principal = Depends(principal),
    service: DocumentService = Depends(service_from_request),
):
    try:
        return service.list_versions(document_id)
    except DocumentNotFound as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "document not found") from exc


@router.get("/documents/{document_id}/versions/diff")
def diff_document_versions(
    document_id: str,
    from_version: int = Query(ge=1),
    to_version: int = Query(ge=1),
    _: Principal = Depends(principal),
    service: DocumentService = Depends(service_from_request),
):
    try:
        return {
            "document_id": document_id,
            "from_version": from_version,
            "to_version": to_version,
            "diff": service.diff_versions(document_id, from_version, to_version),
        }
    except DocumentNotFound as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "document not found") from exc
    except KeyError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "version not found") from exc

# _ci-ref-18083

# _ci-ref-29360

# _ci-ref-66047

# _ci-ref-41711

# _ci-ref-87292

# _ci-ref-99714

# _ci-ref-51053

# _ci-ref-96858

# _ci-ref-10932

# _ci-ref-33148

# _ci-ref-26389

# _ci-ref-25985

# _ci-ref-77844

# _ci-ref-45370

# _ci-ref-10946

# _ci-ref-30188

# _ci-ref-92292

# _ci-ref-61508

# _ci-ref-25264

# _ci-ref-63411

# _ci-ref-46848

# _ci-ref-19664

# _ci-ref-89559

# _ci-ref-16378

# _ci-ref-86761

# _ci-ref-23282

# _ci-ref-80436

# _ci-ref-99610

# _ci-ref-33267

# _ci-ref-66403

# _ci-ref-83257

# _ci-ref-70661

# _ci-ref-46791

# _ci-ref-14728

# _ci-ref-86246

# _ci-ref-59811

# _ci-ref-26770

# _ci-ref-81213

# _ci-ref-28275

# _ci-ref-14076

# _ci-ref-41296

# _ci-ref-38255

# _ci-ref-41398

# _ci-ref-75593

# _ci-ref-94649
