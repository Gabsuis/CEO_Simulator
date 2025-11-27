"""
Document Tools for ADK Agents

Exposes the document service as ADK FunctionTools that agents can use
to access documents based on their role permissions.
"""

import sys
from pathlib import Path
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from google.adk.tools import FunctionTool
from Documents.services.document_service import get_document_service


def create_document_lookup_tool(role_id: str) -> FunctionTool:
    """
    Create a document lookup tool for a specific role.
    
    The tool respects role-based access control defined in the document service.
    
    Args:
        role_id: Role identifier (e.g., 'tech_cofounder', 'advisor', 'vc')
    
    Returns:
        FunctionTool that can look up documents
    """
    doc_service = get_document_service()
    
    def lookup_document(doc_id: str) -> Dict[str, Any]:
        """
        Look up a document by ID.
        
        Args:
            doc_id: Document identifier (e.g., 'financial_report_12m_budget_simulation', 'company_profile')
        
        Returns:
            Document content if accessible, error message otherwise
        """
        # Normalize doc_id: remove file extension, lowercase, replace spaces with underscores
        doc_id_normalized = doc_id.lower().strip()
        doc_id_normalized = doc_id_normalized.replace(' ', '_')
        
        # Remove common file extensions
        for ext in ['.docx', '.xlsx', '.pdf', '.yaml', '.json', '.md', '.txt']:
            if doc_id_normalized.endswith(ext):
                doc_id_normalized = doc_id_normalized[:-len(ext)]
                break
        
        # Check access with normalized ID
        if not doc_service.has_access(role_id, doc_id_normalized):
            # Try to find similar documents
            accessible = doc_service.list_accessible_documents(role_id)
            suggestions = [d['id'] for d in accessible if doc_id.lower() in d['id'] or d['id'] in doc_id.lower()]
            
            suggestion_text = ""
            if suggestions:
                suggestion_text = f"\n\nDid you mean one of these?\n" + "\n".join([f"  - {s}" for s in suggestions[:3]])
            
            return {
                "status": "access_denied",
                "message": f"Cannot access document '{doc_id}' (normalized to '{doc_id_normalized}').{suggestion_text}",
                "suggestions": suggestions[:3]
            }
        
        # Get content with normalized ID
        content = doc_service.get_for_llm(doc_id_normalized, role_id)
        
        if content:
            # Truncate if too long (ADK has token limits)
            max_length = 8000
            if len(content) > max_length:
                content = content[:max_length] + f"\n\n[Document truncated - {len(content)} total characters]"
            
            return {
                "status": "found",
                "doc_id": doc_id_normalized,
                "original_query": doc_id,
                "content": content,
                "length": len(content)
            }
        else:
            # Document not found - provide helpful suggestions
            accessible = doc_service.list_accessible_documents(role_id)
            all_ids = [d['id'] for d in accessible]
            
            return {
                "status": "not_found",
                "message": f"Document '{doc_id_normalized}' not found. Available documents: {', '.join(all_ids[:5])}...",
                "available_documents": all_ids
            }
    
    return FunctionTool(lookup_document)


def create_list_documents_tool(role_id: str) -> FunctionTool:
    """
    Create a tool to list all documents accessible to a role.
    
    Args:
        role_id: Role identifier
    
    Returns:
        FunctionTool that lists accessible documents
    """
    doc_service = get_document_service()
    
    def list_documents() -> Dict[str, Any]:
        """
        List all documents accessible to this role.
        
        Returns:
            List of documents with metadata
        """
        docs = doc_service.list_accessible_documents(role_id)
        
        return {
            "role": role_id,
            "total": len(docs),
            "documents": [
                {
                    "id": d['id'],
                    "title": d['title'],
                    "type": d['type'],
                    "category": d.get('category', 'unknown')
                }
                for d in docs
            ]
        }
    
    return FunctionTool(list_documents)


def create_search_documents_tool(role_id: str) -> FunctionTool:
    """
    Create a tool to search documents by keyword.
    
    Args:
        role_id: Role identifier
    
    Returns:
        FunctionTool that searches documents
    """
    doc_service = get_document_service()
    
    def search_documents(keyword: str) -> Dict[str, Any]:
        """
        Search for documents by keyword in title or category.
        
        Args:
            keyword: Search term
        
        Returns:
            Matching documents
        """
        all_docs = doc_service.list_accessible_documents(role_id)
        keyword_lower = keyword.lower()
        
        matches = [
            d for d in all_docs
            if keyword_lower in d['title'].lower() or 
               keyword_lower in d.get('category', '').lower() or
               keyword_lower in d['type'].lower()
        ]
        
        return {
            "keyword": keyword,
            "total_matches": len(matches),
            "documents": [
                {
                    "id": d['id'],
                    "title": d['title'],
                    "type": d['type'],
                    "category": d.get('category', 'unknown')
                }
                for d in matches
            ]
        }
    
    return FunctionTool(search_documents)


# Test function
if __name__ == "__main__":
    print("Testing document tools...")
    
    try:
        # Test tech cofounder tools
        tech_lookup = create_document_lookup_tool("tech_cofounder")
        tech_list = create_list_documents_tool("tech_cofounder")
        
        print("✅ Created Tech Cofounder document tools")
        
        # Test lookup
        result = tech_lookup.function("company_profile")
        print(f"   Lookup test: {result['status']}")
        
        # Test list
        result = tech_list.function()
        print(f"   List test: {result['total']} documents accessible")
        
        # Test VC tools (limited access)
        vc_lookup = create_document_lookup_tool("vc")
        vc_list = create_list_documents_tool("vc")
        
        print("✅ Created VC document tools")
        
        result = vc_list.function()
        print(f"   VC has access to: {result['total']} documents")
        
        print("\n🎉 All document tools created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating document tools: {e}")
        import traceback
        traceback.print_exc()

