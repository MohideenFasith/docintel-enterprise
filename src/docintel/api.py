from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request, Response, status

from .errors import (
    DocumentNotFound,
    DuplicateDocument,
    InvalidDocument,
    PermissionDenied,
    RateLimitExceeded,
    WorkflowNotFound,
)
from .models import DocumentIn, DocumentPatch, SavedSearchIn, WorkflowRule
from .security import ApiKeyAuthenticator, Principal, SlidingWindowRateLimiter
from .saved_searches import SavedSearchNotFound
from .service import DocumentService


router = APIRouter()


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
