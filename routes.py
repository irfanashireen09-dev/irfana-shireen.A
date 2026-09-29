from fastapi import APIRouter, HTTPException

from backend.ai_core.gemini_generator import GeminiDocumentGenerator
from backend.schemas import DocumentRequest, DocumentResponse


router = APIRouter()


@router.get("/health")
def health():
    return {
        "status": "ok",
        "service": "LegalEase API"
    }


@router.post("/generate", response_model=DocumentResponse)
def generate_document(request: DocumentRequest):
    try:
        generator = GeminiDocumentGenerator()

        content = generator.generate_document(
            document_type=request.document_type,
            parties=request.parties,
            terms=request.terms,
            effective_date=request.effective_date,
            branding=request.branding,
        )

        return DocumentResponse(
            document_type=request.document_type,
            content=content
        )

    except RuntimeError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc)
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Document generation failed: {exc}"
        ) from exc