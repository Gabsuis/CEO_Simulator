# 🎮 CEO Simulator

An advanced AI-powered simulation platform where you role-play as a CEO navigating realistic business scenarios with a team of distinct AI characters. Built with Google Gemini and the Google ADK (Agent Development Kit).

## ✨ Features

- **8 Distinct AI Characters** with unique personalities, speech patterns, and perspectives:
  - **Sarai** - Meta-orchestrator with access to all sessions
  - **Omer** - Tech Cofounder (pragmatic, protective)
  - **Sol** - Advisor (wise, questioning)
  - **Roni** - Marketing Cofounder (passionate, customer-focused)
  - **Sami** - VC (direct, skeptical)
  - **Shaar** - Executive Coach (warm, reflective)
  - **3x Therapist Personas** - Customer perspectives

- **Multi-Session Architecture** with role-based access:
  - `all_knowing` - Sarai sees everything
  - `radical_transparency` - Tech, Advisor, Marketing share a session
  - `private` - VC, Coach, Therapists have isolated sessions

- **Rich Document Knowledge Base**:
  - Company profile, financial reports, product roadmap
  - Engineering specs, marketing materials, customer research
  - Role-based access control

- **Interactive Chat Interface**:
  - Web UI via Streamlit
  - Agent switching without interruption
  - Automatic conversation logging
  - Transcript export

## 🚀 Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/CEO_Simulator.git
   cd CEO_Simulator
   ```

2. **Create Python virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up your API key**
   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   # Edit .streamlit/secrets.toml and add your GOOGLE_API_KEY
   ```

5. **Run the Streamlit app**
   ```bash
   streamlit run streamlit_app.py
   ```

6. **Open browser**
   - Navigate to `http://localhost:8501`

### Deploy to Streamlit Cloud

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Initial CEO Simulator deployment"
   git push origin main
   ```

2. **Create Streamlit Cloud account**
   - Go to https://share.streamlit.io/
   - Sign in with GitHub

3. **Deploy your app**
   - Click "New app"
   - Select your repo, branch, and select `streamlit_app.py`
   - Click "Deploy"

4. **Add secrets**
   - In app settings → Secrets
   - Paste your `GOOGLE_API_KEY`

5. **Share your link!**
   - Your app is now live at `https://your-app.streamlit.app`

## 📁 Project Structure

```
CEO_Simulator/
├── streamlit_app.py              # Web UI entry point
├── simulation_engine_adk.py      # Core simulation engine
├── interactive_chat.py           # CLI interface (local development)
│
├── adk_agents/                   # AI Agent implementations
│   ├── role_agents.py            # Tech, Advisor, Marketing agents
│   ├── sarai_agent.py            # Meta-orchestrator
│   ├── scene_context.py          # Scene-specific context injection
│   └── document_tools.py         # Document lookup tools
│
├── characters/                   # Character specifications (YAML)
│   ├── character_registry.yaml
│   ├── tech_cofounder/
│   ├── advisor/
│   ├── marketing_cofounder/
│   ├── vc/
│   ├── coach/
│   ├── sarai/
│   └── therapist_customers/
│
├── scenes/                       # Simulation scenarios
│   ├── scene_registry.yaml
│   └── scene1/
│       └── scene_config.yaml
│
├── Documents/                    # Knowledge base
│   ├── services/
│   │   └── document_service.py   # Document indexing & access
│   ├── assets/
│   │   ├── markdown/             # Converted documents
│   │   └── documents/
│   │       ├── document__index.json
│   │       └── *.docx, *.xlsx, *.pdf
│   └── resources/
│       └── document_index.json
│
├── engine/                       # Loaders & utilities
│   ├── character_loader.py
│   ├── scene_loader.py
│   └── __init__.py
│
├── .streamlit/                   # Streamlit configuration
│   ├── config.toml
│   ├── secrets.toml.example      # ← Copy and add your API key
│   └── secrets.toml              # ← Created locally (gitignored)
│
├── requirements.txt              # Python dependencies
├── .gitignore                    # Git configuration
└── README.md                     # This file
```

## 🎯 Usage Examples

### Chat with a specific character

```python
# Start with the Streamlit app
streamlit run streamlit_app.py

# Or use the CLI for development
python interactive_chat.py
```

### Add a new scene

1. Create `scenes/scene2/` folder
2. Add `scene_config.yaml` with scene context
3. Update `scenes/scene_registry.yaml`
4. Characters automatically adapt to new scene

### Add a new character

1. Create `characters/new_character/` folder
2. Add `character_spec.yaml` with personality, mandate, etc.
3. Update `characters/character_registry.yaml`
4. Update `adk_agents/role_agents.py` with creation function

## 🔧 Configuration

### Character Customization

Edit `characters/{character}/character_spec.yaml`:

```yaml
identity:
  name: "Character Name"
  tagline: "Character focus/role"
  backstory: "Character history"

personality:
  traits:
    - "Trait 1"
    - "Trait 2"
  quirks:
    - "Unique quirk or mannerism"
  speech_patterns:
    - "Common phrase or pattern"

emotional_context:
  current_mood: "Current emotional state"
  underlying_concerns:
    - "What's on their mind"
  motivations:
    - "What drives them"
```

### Document Access

Edit character specs to control document visibility:

```yaml
knowledge_core:
  sees:
    - "company_profile"
    - "financial_report"
    - "product_roadmap"
```

## 🌐 Deployment Options

| Platform | Cost | Setup Time | Best For |
|----------|------|-----------|----------|
| **Streamlit Cloud** | Free | 5 min | Quick demos, portfolios |
| **Google Cloud Run** | $~0-20/mo | 30 min | Production, custom domains |
| **Local/VPS** | Varies | 1 hour | Full control, private |

## 🔐 Security & API Keys

⚠️ **IMPORTANT**: Never commit your API key to GitHub!

1. **Locally**: Create `.streamlit/secrets.toml` (gitignored)
2. **Streamlit Cloud**: Add secret in app settings dashboard
3. **Other platforms**: Use environment variables or secrets manager

## 📊 Model Configuration

The simulator uses:
- **Gemini 2.5 Flash** for regular agents (temperature: 0.85)
- **Gemini 3 Pro Preview** for Sarai orchestrator (temperature: 0.2)

Adjust in `adk_agents/role_agents.py` and `adk_agents/sarai_agent.py`.

## 🧪 Testing & Development

### CLI Interactive Chat
```bash
python interactive_chat.py
```

### Debug a specific agent
```bash
python -c "
from adk_agents.role_agents import create_tech_cofounder_agent
tech = create_tech_cofounder_agent()
print(tech.instruction)
"
```

## 📝 Conversation Transcripts

All conversations are saved to `transcripts/chat_transcript_YYYYMMDD_HHMMSS.txt`

## 🤝 Contributing

Contributions welcome! Areas to enhance:
- Additional scenes and scenarios
- More character personas
- Improved document ingestion pipeline
- Enhanced analytics dashboard
- Mobile-responsive UI

## 📞 Support

For issues or questions:
1. Check existing GitHub issues
2. Create a new issue with details
3. Include error logs from `transcripts/`

## 📄 License

[Add your license here - e.g., MIT]

## 🙏 Acknowledgments

Built with:
- [Google Gemini](https://gemini.google.com/)
- [Google ADK (Agent Development Kit)](https://github.com/google/adk)
- [Streamlit](https://streamlit.io/)

---

**Happy simulating! 🚀**

