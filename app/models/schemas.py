from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class IngestFileRequest(BaseModel):
    """Payload to request the ingestion of a single specific document."""
    file_path: str = Field(..., description="Absolute or relative path to the local document file (PDF, TXT, MD)")
    collection_name: Optional[str] = Field(None, description="Optional target vector collection name override")

class IngestFolderRequest(BaseModel):
    """Payload to request ingestion of an entire folder recursively."""
    folder_path: str = Field(..., description="Absolute or relative path to the local directory containing documents")
    collection_name: Optional[str] = Field(None, description="Optional target vector collection name override")

class IngestResponse(BaseModel):
    """Response containing ingestion results."""
    success: bool
    nodes_ingested: int
    message: str

class QueryRequest(BaseModel):
    """Payload to execute a full context-augmented LLM query."""
    prompt: str = Field(..., description="The query question to ask the local RAG engine")
    collection_name: Optional[str] = Field(None, description="Optional target collection override")
    system_prompt: Optional[str] = Field(None, description="Optional system prompt override (e.g. for German optimization)")

class QueryResponse(BaseModel):
    """Response returned from a full LLM RAG query."""
    answer: str
    collection: str
    model_used: str

class SearchRequest(BaseModel):
    """Payload to execute pure semantic retrieval without calling the LLM."""
    query: str = Field(..., description="Term or sentence to match semantically")
    limit: int = Field(5, description="Maximum number of context nodes to retrieve")
    collection_name: Optional[str] = Field(None, description="Optional target collection override")

class SearchResultNode(BaseModel):
    """A single matching context block retrieved from Qdrant."""
    node_id: str
    text: str
    score: float
    metadata: Dict[str, Any] = Field(default_factory=dict)

class SearchResponse(BaseModel):
    """Response containing raw semantic search matches."""
    query: str
    results: List[SearchResultNode]
