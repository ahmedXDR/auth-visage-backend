from uuid import UUID

from fastapi import APIRouter

from app.api.deps import CurrentUser, SessionDep
from app.crud import project
from app.models.project import Project, ProjectCreate, ProjectUpdate

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/create-project")
async def create_project(
    project_in: ProjectCreate,
    user: CurrentUser,
    session: SessionDep,
) -> Project:
    return project.create(session, owner_id=UUID(user.id), obj_in=project_in)


@router.get("/get-project/{id}")
async def read_project_by_id(id: str, session: SessionDep) -> Project | None:
    return project.get(session, id=UUID(id))


@router.get("/get-projects")
async def read_projects(
    session: SessionDep, skip: int = 0, limit: int = 100
) -> list[Project]:
    return list(project.get_multi(session, skip=skip, limit=limit))


@router.put("/update-project/{id}")
async def update_project(
    id: str,
    project_in: ProjectUpdate,
    session: SessionDep,
) -> Project | None:
    return project.update(session, id=UUID(id), obj_in=project_in)


@router.delete("/delete/{id}")
async def delete_project(id: str, session: SessionDep) -> Project | None:
    return project.remove(session, id=UUID(id))
