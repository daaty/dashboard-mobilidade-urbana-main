from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.db import SessionLocal
from app.models.campanha import Campanha
from app.schemas.campanha import CampanhaCreate, CampanhaUpdate, CampanhaOut
from typing import List
from datetime import datetime

router = APIRouter()

async def get_async_db():
    async with SessionLocal() as session:
        yield session

@router.get("/campanhas", response_model=List[CampanhaOut])
async def listar_campanhas(db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(Campanha))
    return result.scalars().all()

@router.post("/campanhas", response_model=CampanhaOut)
async def criar_campanha(campanha: CampanhaCreate, db: AsyncSession = Depends(get_async_db)):
    nova = Campanha(**campanha.dict(), created_at=datetime.utcnow())
    db.add(nova)
    await db.commit()
    await db.refresh(nova)
    return nova

@router.put("/campanhas/{campanha_id}", response_model=CampanhaOut)
async def atualizar_campanha(campanha_id: int, campanha: CampanhaUpdate, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(Campanha).where(Campanha.id == campanha_id))
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Campanha não encontrada")
    for k, v in campanha.dict().items():
        setattr(obj, k, v)
    await db.commit()
    await db.refresh(obj)
    return obj

@router.delete("/campanhas/{campanha_id}")
async def deletar_campanha(campanha_id: int, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(Campanha).where(Campanha.id == campanha_id))
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Campanha não encontrada")
    await db.delete(obj)
    await db.commit()
    return {"ok": True}
