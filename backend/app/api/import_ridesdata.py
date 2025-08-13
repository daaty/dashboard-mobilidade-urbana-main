from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database.db import get_db
from services.import_ridesdata_simple import ImportService
import os

router = APIRouter()

@router.post("/import/ridesdata")
async def import_ridesdata_endpoint(
    file: UploadFile = File(...),
    table_name: str = Form(...),
    db: Session = Depends(get_db)
):
    """Endpoint para importar planilha direto para rides_data"""
    try:
        service = ImportService()
        # Salvar arquivo temporário
        filename = file.filename
        os.makedirs("uploads", exist_ok=True)  # Garantir que a pasta existe
        temp_path = os.path.join("uploads", filename)
        with open(temp_path, "wb") as f:
            f.write(await file.read())
        # Importar para rides_data
        result = service.import_ridesdata(temp_path, table_name, session=db)
        # Remover arquivo temporário
        if os.path.exists(temp_path):
            os.remove(temp_path)
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        return {"success": True, "imported": result['imported']}
    except Exception as e:
        # Log do erro para debug
        print(f"Erro no endpoint import_ridesdata: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
