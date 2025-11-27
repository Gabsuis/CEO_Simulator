# Documents Package

This package contains all simulation documents in both original and LLM-readable formats.

## Structure

```
Documents/
├── assets/
│   ├── documents/           # Original binary files (Excel, Word, PDF)
│   ├── markdown/            # LLM-readable markdown versions
│   └── summaries/           # Quick summaries for each document
├── scripts/
│   └── convert_documents.py # Conversion utility
├── services/
│   └── document_service.py  # Document access service
└── README.md
```

## Document Formats

### Original Files (`assets/documents/`)
- **Excel (.xlsx)**: Financial models, backlogs, sprint plans
- **Word (.docx)**: Product specs, engineering reports, process docs
- **PDF**: Feature specs, website briefing, coaching references
- **YAML**: Company profile, roadmap, therapist personas

### Markdown Versions (`assets/markdown/`)
- LLM-readable format with tables, headings, and structure
- Generated automatically from originals
- Used by simulation agents for context

### Summaries (`assets/summaries/`)
- First 500 characters of each document
- Quick reference for document selection

## Usage

### For LLMs (Simulation Agents)

```python
from services.document_service import get_document_service

doc_service = get_document_service()

# Get document for a specific role
content = doc_service.get_for_llm('financial_report_12m_budget_simulation', 'advisor')

# Get all accessible documents for a role
context = doc_service.get_all_for_role_context('tech_cofounder')

# List what a role can see
docs = doc_service.list_accessible_documents('vc')
```

### For UI (User Interface)

```python
# Get document with metadata for rendering
doc_data = doc_service.get_for_ui('product_vision', user_id='user123', role_id='advisor')

# Returns:
# {
#   'id': 'product_vision',
#   'title': 'Mentalyc Product Vision',
#   'type': 'marketing',
#   'content': '# Mentalyc Product Vision\n\n...',
#   'download_url': '/api/documents/product_vision/download',
#   'llm_readable': True,
#   'user_viewable': True
# }
```

## Document Access Rules

### Tier 1: All-Knowing
- **Sarai**: ALL documents

### Tier 2: Radical Transparency
- **Advisor**: Core canon + ALL company docs + strategy refs + financials + roadmap
- **Tech Cofounder**: Core canon + engineering docs + backlogs + tech debt + compliance
- **Marketing Cofounder**: Core canon + GTM docs + website + positioning + therapist personas

### Tier 3: Private
- **VC**: Core canon + board-level financials + high-level roadmap ONLY
- **Coach**: Core canon + coaching refs + CEO evaluations (generated)
- **Therapists**: Core canon ONLY

**Core Canon (Everyone):**
- `company_profile`
- `product_vision`
- `product_goal`

## Converting Documents

To regenerate markdown versions after updating source documents:

```bash
cd Documents
python scripts/convert_documents.py
```

This will:
1. Convert all Excel, Word, and PDF files to markdown
2. Generate summaries
3. Update `document__index.json` with format paths

## Adding New Documents

1. Add the original file to `assets/documents/`
2. Add entry to `document__index.json`:

```json
{
  "id": "new_document",
  "title": "New Document Title",
  "file": "assets/documents/New_Document.xlsx",
  "type": "financial",
  "category": "operations",
  "summary": "Brief description"
}
```

3. Run conversion script:
```bash
python scripts/convert_documents.py
```

4. Update access rules in `services/document_service.py` if needed

## Document Types

- **financial**: Financial models, budgets, burn rates
- **engineering**: Backlogs, status reports, technical specs
- **marketing**: GTM plans, website content, positioning
- **product**: Vision, goals, roadmaps, feature specs
- **operations**: Process docs, definitions, cadences
- **reference**: Coaching materials, research, personas

## Dependencies

```bash
pip install openpyxl pandas python-docx pypdf tabulate
```

## Integration with Simulation Engine

The document service integrates with the YAML Simulator 2 engine:

1. **Engine loads specs** → determines role access rules
2. **Role makes request** → engine checks `session_access.mode`
3. **Document service** → serves markdown to LLM based on role
4. **LLM generates response** → using document context
5. **UI displays** → rendered markdown + download link to original

## File Locations

- **Original files**: Keep in `assets/documents/` for audit/download
- **Markdown files**: Auto-generated in `assets/markdown/`
- **Summaries**: Auto-generated in `assets/summaries/`
- **Index**: `assets/documents/document__index.json`

## Notes

- Markdown files are regenerated on conversion, don't edit manually
- Original files are source of truth
- Access control is enforced at service level
- UI can display markdown with rich formatting (tables, headings, etc.)

