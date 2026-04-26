from __future__ import annotations
from fastapi import APIRouter, HTTPException, status
from app.api.deps import CurrentUser, DbDep
from app.schemas.collection import CollectionResponse, CreateCollectionRequest
from app.services import collection_service

router = APIRouter()


@router.post("", response_model=CollectionResponse, status_code=status.HTTP_201_CREATED)
async def create_collection(req: CreateCollectionRequest, current_user: CurrentUser, db: DbDep):
    try:
        collection = await collection_service.create_collection(
            db, req.name, req.description, current_user.id
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    return CollectionResponse.model_validate(collection)


@router.get("", response_model=list[CollectionResponse])
async def list_collections(_: CurrentUser, db: DbDep):
    collections = await collection_service.list_collections(db)
    return [CollectionResponse.model_validate(c) for c in collections]


@router.get("/{collection_id}", response_model=CollectionResponse)
async def get_collection(collection_id: int, _: CurrentUser, db: DbDep):
    collection = await collection_service.get_collection(db, collection_id)
    if not collection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found")
    return CollectionResponse.model_validate(collection)


@router.delete("/{collection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_collection(collection_id: int, current_user: CurrentUser, db: DbDep):
    collection = await collection_service.get_collection(db, collection_id)
    if not collection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found")
    if collection.owner_id != current_user.id and current_user.role.name != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your collection")
    try:
        await collection_service.delete_collection(db, collection_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
