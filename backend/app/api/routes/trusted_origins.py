from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.api.deps import CurrentUser, SessionDep
from app.crud import project, trusted_origin
from app.models.trusted_origin import (
    TrustedOrigin,
    TrustedOriginCreate,
    TrustedOriginUpdate,
)

router = APIRouter(prefix="/trusted-origins", tags=["trusted-origins"])


@router.post(
    "/create-trusted-origin",
    response_model=TrustedOrigin,
)
async def create_trusted_origin(
    trusted_origin_in: TrustedOriginCreate,
    user: CurrentUser,
    session: SessionDep,
) -> TrustedOrigin:
    project_obj = project.get(session, id=trusted_origin_in.project_id)
    if project_obj is None:
        raise HTTPException(status_code=404, detail="Project not found")
    if project_obj.owner_id != UUID(user.id):
        raise HTTPException(status_code=403, detail="Unauthorized")

    return trusted_origin.create(
        session,
        obj_in=trusted_origin_in,
        owner_id=UUID(user.id),
    )


@router.get(
    "/get-trusted-origin/{id}",
    response_model=TrustedOrigin | None,
)
async def read_trusted_origin_by_id(
    id: str,
    session: SessionDep,
    user: CurrentUser,
) -> TrustedOrigin | None:
    trusted_origin_obj = trusted_origin.get(session, id=UUID(id))
    if trusted_origin_obj:
        if trusted_origin_obj.owner_id != UUID(user.id):
            raise HTTPException(status_code=403, detail="Unauthorized")
    return trusted_origin_obj


@router.get(
    "/get-trusted-origins",
    response_model=list[TrustedOrigin],
)
async def read_trusted_origins(
    session: SessionDep,
    user: CurrentUser,
    project_id: str,
    skip: int = 0,
    limit: int = 100,
) -> list[TrustedOrigin]:
    trusted_origins = trusted_origin.get_multi_by_owner_and_project(
        session,
        owner_id=UUID(user.id),
        project_id=UUID(project_id),
        skip=skip,
        limit=limit,
    )
    return list(trusted_origins)


@router.put(
    "/update-trusted-origin/{id}",
    response_model=TrustedOrigin | None,
)
async def update_project(
    id: str,
    trusted_origin_in: TrustedOriginUpdate,
    user: CurrentUser,
    session: SessionDep,
) -> TrustedOrigin | None:
    trusted_origin_obj = trusted_origin.get(session, id=UUID(id))
    if trusted_origin_obj:
        if trusted_origin_obj.owner_id != UUID(user.id):
            raise HTTPException(status_code=403, detail="Unauthorized")

    if trusted_origin_in.project_id is not None:
        project_obj = project.get(session, id=trusted_origin_in.project_id)
        if project_obj is None:
            raise HTTPException(status_code=404, detail="Project not found")
        if project_obj.owner_id != UUID(user.id):
            raise HTTPException(status_code=403, detail="Unauthorized")

    return trusted_origin.update(
        session, id=UUID(id), obj_in=trusted_origin_in
    )


@router.delete(
    "/delete/{id}",
    response_model=TrustedOrigin | None,
)
async def delete_trusted_origin(
    id: str,
    user: CurrentUser,
    session: SessionDep,
) -> TrustedOrigin | None:
    trusted_origin_obj = trusted_origin.get(session, id=UUID(id))
    if trusted_origin_obj:
        if trusted_origin_obj.owner_id != UUID(user.id):
            raise HTTPException(status_code=403, detail="Unauthorized")
    return trusted_origin.remove(session, id=UUID(id))
