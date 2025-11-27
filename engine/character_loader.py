"""
Character Loader

Loads character specifications from the characters/ folder structure.
Provides a clean API for accessing character data.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass


@dataclass
class CharacterSpec:
    """Character specification data."""
    id: str
    name: str
    folder: str
    role: str
    session_tier: str
    description: str
    spec_data: Dict[str, Any]
    base_path: Path
    
    def get_portrait_path(self) -> Optional[Path]:
        """Get path to character portrait image."""
        for ext in ['.png', '.jpg', '.jpeg', '.webp']:
            portrait_path = self.base_path / f"portrait{ext}"
            if portrait_path.exists():
                return portrait_path
        return None
    
    def get_knowledge_core(self) -> Dict[str, Any]:
        """Get knowledge_core section from spec."""
        return self.spec_data.get('knowledge_core', {})
    
    def get_documents_sees(self) -> List[str]:
        """Get list of documents this character should see."""
        knowledge_core = self.get_knowledge_core()
        return knowledge_core.get('sees', [])
    
    def get_mandate(self) -> Dict[str, Any]:
        """Get mandate section from spec."""
        return self.spec_data.get('mandate', {})
    
    def get_identity(self) -> Dict[str, Any]:
        """Get identity section from spec."""
        return self.spec_data.get('identity', {})
    
    def get_interaction_patterns(self) -> Dict[str, Any]:
        """Get interaction_patterns section from spec."""
        return self.spec_data.get('interaction_patterns', {})


class CharacterLoader:
    """Loads and manages character specifications."""
    
    def __init__(self, characters_root: Optional[Path] = None):
        """
        Initialize character loader.
        
        Args:
            characters_root: Path to characters/ folder (defaults to project_root/characters)
        """
        if characters_root is None:
            # Default to project_root/characters
            project_root = Path(__file__).parent.parent
            characters_root = project_root / "characters"
        
        self.characters_root = Path(characters_root)
        self.registry = self._load_registry()
    
    def _load_registry(self) -> Dict[str, Any]:
        """Load character registry."""
        registry_path = self.characters_root / "character_registry.yaml"
        
        if not registry_path.exists():
            raise FileNotFoundError(f"Character registry not found: {registry_path}")
        
        with open(registry_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def list_characters(self) -> Dict[str, Dict[str, Any]]:
        """List all available characters."""
        return self.registry.get('characters', {})
    
    def load_character(self, character_id: str) -> CharacterSpec:
        """
        Load a character specification.
        
        Args:
            character_id: Character identifier (e.g., 'tech_cofounder', 'sarai')
        
        Returns:
            CharacterSpec object
        """
        # Get character metadata from registry
        characters = self.registry.get('characters', {})
        if character_id not in characters:
            raise ValueError(f"Unknown character_id: {character_id}")
        
        char_meta = characters[character_id]
        folder = char_meta['folder']
        
        # Load character spec file
        char_path = self.characters_root / folder
        spec_path = char_path / "character_spec.yaml"
        
        if not spec_path.exists():
            raise FileNotFoundError(f"Character spec not found: {spec_path}")
        
        with open(spec_path, 'r', encoding='utf-8') as f:
            # Handle multiple documents and nested structure
            docs = list(yaml.safe_load_all(f))
            spec_data = None
            
            for doc in docs:
                if doc is not None:
                    # Unwrap nested structure (e.g., tech_cofounder_spec: { ... })
                    if f"{character_id}_spec" in doc:
                        spec_data = doc[f"{character_id}_spec"]
                        break
                    else:
                        spec_data = doc
                        break
            
            if spec_data is None:
                raise ValueError(f"No valid YAML document found in {spec_path}")
        
        # Create CharacterSpec object
        return CharacterSpec(
            id=character_id,
            name=char_meta['name'],
            folder=folder,
            role=char_meta['role'],
            session_tier=char_meta['session_tier'],
            description=char_meta['description'],
            spec_data=spec_data,
            base_path=char_path
        )
    
    def get_characters_by_session_tier(self, tier: str) -> List[str]:
        """
        Get list of character IDs for a given session tier.
        
        Args:
            tier: Session tier ('all_knowing', 'radical_transparency', 'private')
        
        Returns:
            List of character IDs
        """
        characters = self.registry.get('characters', {})
        return [
            char_id for char_id, char_data in characters.items()
            if char_data.get('session_tier') == tier
        ]
    
    def get_session_tier_info(self, tier: str) -> Dict[str, Any]:
        """Get information about a session tier."""
        tiers = self.registry.get('session_tiers', {})
        return tiers.get(tier, {})


# Singleton instance
_character_loader = None

def get_character_loader(characters_root: Optional[Path] = None) -> CharacterLoader:
    """Get or create the character loader singleton."""
    global _character_loader
    if _character_loader is None:
        _character_loader = CharacterLoader(characters_root)
    return _character_loader


# Test function
if __name__ == "__main__":
    print("Testing Character Loader...")
    print()
    
    try:
        loader = get_character_loader()
        print(f"✅ Character loader initialized")
        print(f"   Characters root: {loader.characters_root}")
        print()
        
        # List characters
        characters = loader.list_characters()
        print(f"👥 Available characters: {len(characters)}")
        for char_id, char_data in characters.items():
            print(f"   - {char_id}: {char_data['name']} ({char_data['session_tier']})")
        print()
        
        # Load a character
        print(f"🎭 Loading Tech Cofounder...")
        tech = loader.load_character('tech_cofounder')
        print(f"   ✅ Loaded: {tech.name}")
        print(f"   Role: {tech.role}")
        print(f"   Session Tier: {tech.session_tier}")
        print(f"   Documents sees: {len(tech.get_documents_sees())}")
        for doc in tech.get_documents_sees():
            print(f"      - {doc}")
        print()
        
        # Get characters by tier
        print(f"📊 Characters by session tier:")
        for tier in ['all_knowing', 'radical_transparency', 'private']:
            chars = loader.get_characters_by_session_tier(tier)
            print(f"   {tier}: {', '.join(chars)}")
        print()
        
        print("🎉 All tests passed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

