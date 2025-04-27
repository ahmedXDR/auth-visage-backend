from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.api.deps import CurrentUser, SessionDep
from app.crud import project
from app.models.project import Project, ProjectCreate, ProjectUpdate

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post(
    "",
    response_model=Project,
)
async def create_project(
    project_in: ProjectCreate,
    user: CurrentUser,
    session: SessionDep,
) -> Project:
    return project.create(session, owner_id=UUID(user.id), obj_in=project_in)


@router.get(
    "/{id}",
    response_model=Project | None,
)
async def read_project_by_id(
    id: str,
    session: SessionDep,
    user: CurrentUser,
) -> Project | None:
    project_obj = project.get(session, id=UUID(id))
    if project_obj:
        if project_obj.owner_id != UUID(user.id):
            raise HTTPException(status_code=403, detail="Unauthorized")
    return project_obj


@router.get(
    "",
    response_model=list[Project],
)
async def read_projects(
    session: SessionDep,
    user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> list[Project]:
    projects = project.get_multi_by_owner(
        session, owner_id=UUID(user.id), skip=skip, limit=limit
    )
    return list(projects)


@router.put(
    "/{id}",
    response_model=Project | None,
)
async def update_project(
    id: str,
    project_in: ProjectUpdate,
    user: CurrentUser,
    session: SessionDep,
) -> Project | None:
    project_obj = project.get(session, id=UUID(id))
    if project_obj:
        if project_obj.owner_id != UUID(user.id):
            raise HTTPException(status_code=403, detail="Unauthorized")
    return project.update(session, id=UUID(id), obj_in=project_in)


@router.delete(
    "/{id}",
    response_model=Project | None,
)
async def delete_project(
    id: str,
    user: CurrentUser,
    session: SessionDep,
) -> Project | None:
    project_obj = project.get(session, id=UUID(id))
    if project_obj:
        if project_obj.owner_id != UUID(user.id):
            raise HTTPException(status_code=403, detail="Unauthorized")
    return project.remove(session, id=UUID(id))
