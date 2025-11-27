"""
Document Service for YAML Simulator 2

Provides document access control and serves markdown versions to LLMs
while preserving original files for UI download.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any


class DocumentService:
    """
    Manages document access and serves content in appropriate formats.
    
    - LLMs get markdown versions
    - UI gets metadata + markdown for rendering
    - Access control based on role specs
    """
    
    def __init__(self, base_path: str = None):
        if base_path is None:
            base_path = Path(__file__).parent.parent
        
        self.base_path = Path(base_path)
        self.docs_dir = self.base_path / "assets" / "documents"
        self.markdown_dir = self.base_path / "assets" / "markdown"
        self.summaries_dir = self.base_path / "assets" / "summaries"
        self.resources_dir = self.base_path / "resources"
        
        # Load document index (company documents)
        index_path = self.docs_dir / "document__index.json"
        with open(index_path, 'r', encoding='utf-8') as f:
            index_data = json.load(f)
        
        self.documents = {doc['id']: doc for doc in index_data['documents']}
        self.meta = index_data.get('meta', {})
        
        # Load resources index (reference materials)
        resources_index_path = self.resources_dir / "document_index.json"
        if resources_index_path.exists():
            with open(resources_index_path, 'r', encoding='utf-8') as f:
                resources_data = json.load(f)
            
            # Add resources to documents dict
            for doc in resources_data['documents']:
                self.documents[doc['id']] = doc
        
        # Define access rules based on role specs
        self.access_rules = self._build_access_rules()
    
    def _build_access_rules(self) -> Dict[str, List[str]]:
        """Build document access rules from role specifications."""
        return {
            # Tier 1: All-knowing
            'sarai': ['*'],  # Sees everything
            
            # Tier 2: Radical transparency
            'advisor': [
                'company_profile', 'product_vision', 'product_goal',
                'financial_report_12m_budget_simulation',
                'mentalyc_6_sprint_backlog', 'mentalyc_backlog_sprints_1_2',
                'mentalyc_product_backlog', 'mentalyc_product_goal',
                'mentalyc_product_vision', 'tech_backlog_8weeks',
                'mentalyc_marketing_sprint_plan', 'mentalyc_9_month_product_roadmap',
                # Resources
                'startup_ceo_textbook',
                'article:_product_risk_taxonomy___silicon_valley_product_group',
                'the_purpose_of_prototypes___silicon_valley_product_group',
                '8_article_series___what_now_v2'
            ],
            'tech_cofounder': [
                'company_profile', 'product_vision', 'product_goal',
                'mentalyc_product_backlog', 'mentalyc_6_sprint_backlog',
                'mentalyc_6_sprint_realworld_analytics',
                'mentalyc_backlog_sprints_1_2',
                'mentalyc_engineering_status_report_sprints_1_2',
                'tech_backlog_sprint_summary', 'tech_backlog_8weeks',
                'poc_must-have_features', 'mentalyc_definition_of_done',
                'mentalyc_scrum_roles', 'mentalyc_sprint_cadence',
                'mentalyc_engineering_website_sprint_plan',
                # Resources
                'technology_ventures_byers_dorf_nelson_4th_edition',
                'the_purpose_of_prototypes___silicon_valley_product_group'
            ],
            'marketing_cofounder': [
                'company_profile', 'product_vision', 'product_goal',
                'mentalyc_product_vision', 'mentalyc_product_goal',
                'mentalyc_marketing_sprint_plan',
                'mentalyc_engineering_website_sprint_plan',
                'website_briefing', 'therapists',
                'mentalyc_marketing_risk_memo_to_engineering'
            ],
            
            # Tier 3: Private
            'vc': [
                'company_profile', 'product_vision', 'product_goal',
                'financial_report_12m_budget_simulation',  # board-level only
                'mentalyc_9_month_product_roadmap'  # high-level roadmap
            ],
            'coach': [
                'company_profile', 'product_vision', 'product_goal',
                # Resources
                'enterprise_coaching_book_silas_de_la_maza_kudinov__draft_manuscript',
                'zen_coach_reference_guide_and_ai_prompt_pack',
                # CEO evaluations and meeting summaries added dynamically
            ],
            'therapist_1': [
                'company_profile', 'product_vision', 'product_goal'
            ],
            'therapist_2': [
                'company_profile', 'product_vision', 'product_goal'
            ],
            'therapist_3': [
                'company_profile', 'product_vision', 'product_goal'
            ],
        }
    
    def has_access(self, role_id: str, doc_id: str) -> bool:
        """Check if a role has access to a document."""
        if role_id not in self.access_rules:
            return False
        
        role_docs = self.access_rules[role_id]
        
        # Sarai sees everything
        if '*' in role_docs:
            return True
        
        return doc_id in role_docs
    
    def get_for_llm(self, doc_id: str, role_id: str) -> Optional[str]:
        """
        Get document content in markdown format for LLM consumption.
        
        Args:
            doc_id: Document identifier
            role_id: Role requesting the document
        
        Returns:
            Markdown content or None if no access
        """
        if not self.has_access(role_id, doc_id):
            return None
        
        if doc_id not in self.documents:
            return None
        
        doc = self.documents[doc_id]
        
        # Load markdown version
        if 'formats' in doc and 'markdown' in doc['formats']:
            md_path = self.base_path / doc['formats']['markdown']
            if md_path.exists():
                return md_path.read_text(encoding='utf-8')
        
        return None
    
    def get_summary(self, doc_id: str, role_id: str) -> Optional[str]:
        """Get document summary for quick reference."""
        if not self.has_access(role_id, doc_id):
            return None
        
        if doc_id not in self.documents:
            return None
        
        doc = self.documents[doc_id]
        
        if 'formats' in doc and 'summary' in doc['formats']:
            summary_path = self.base_path / doc['formats']['summary']
            if summary_path.exists():
                return summary_path.read_text(encoding='utf-8')
        
        return None
    
    def get_for_ui(self, doc_id: str, user_id: str, role_id: str = None) -> Optional[Dict[str, Any]]:
        """
        Get document metadata and content for UI rendering.
        
        Args:
            doc_id: Document identifier
            user_id: User requesting the document
            role_id: Optional role context for access control
        
        Returns:
            Dictionary with document metadata and content
        """
        # If role_id provided, check access
        if role_id and not self.has_access(role_id, doc_id):
            return None
        
        if doc_id not in self.documents:
            return None
        
        doc = self.documents[doc_id]
        
        # Load markdown content
        content = None
        if 'formats' in doc and 'markdown' in doc['formats']:
            md_path = self.base_path / doc['formats']['markdown']
            if md_path.exists():
                content = md_path.read_text(encoding='utf-8')
        
        # Build response
        return {
            'id': doc_id,
            'title': doc['title'],
            'type': doc['type'],
            'category': doc.get('category', 'operations'),
            'content': content,
            'summary': doc.get('summary', ''),
            'original_file': doc.get('file', ''),
            'download_url': f"/api/documents/{doc_id}/download",
            'llm_readable': doc.get('llm_readable', False),
            'user_viewable': doc.get('user_viewable', False)
        }
    
    def list_accessible_documents(self, role_id: str) -> List[Dict[str, Any]]:
        """List all documents accessible to a role."""
        accessible = []
        
        for doc_id, doc in self.documents.items():
            if self.has_access(role_id, doc_id):
                accessible.append({
                    'id': doc_id,
                    'title': doc['title'],
                    'type': doc['type'],
                    'category': doc.get('category', 'operations'),
                    'summary': doc.get('summary', '')
                })
        
        return accessible
    
    def get_all_for_role_context(self, role_id: str, max_length: int = 50000) -> str:
        """
        Get all accessible documents concatenated for LLM context.
        Useful for loading role's full knowledge base.
        
        Args:
            role_id: Role identifier
            max_length: Maximum total character length
        
        Returns:
            Concatenated markdown of all accessible documents
        """
        context = f"# Document Context for {role_id}\n\n"
        current_length = len(context)
        
        for doc_id in self.access_rules.get(role_id, []):
            if doc_id == '*':
                # Don't load everything for Sarai automatically
                continue
            
            content = self.get_for_llm(doc_id, role_id)
            if content:
                # Check if adding this would exceed limit
                if current_length + len(content) > max_length:
                    context += f"\n\n---\n\n*[Additional documents truncated due to length]*\n"
                    break
                
                context += f"\n\n---\n\n{content}\n\n"
                current_length += len(content)
        
        return context


# Singleton instance
_document_service = None

def get_document_service(base_path: str = None) -> DocumentService:
    """Get or create the document service singleton."""
    global _document_service
    if _document_service is None:
        _document_service = DocumentService(base_path)
    return _document_service

