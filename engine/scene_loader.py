"""
Scene Loader

Loads scene configurations from the scenes/ folder structure.
Provides a clean API for accessing scene data.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class SceneConfig:
    """Scene configuration data."""
    id: str
    name: str
    title: str
    folder: str
    timeframe: str
    description: str
    active: bool
    config_data: Dict[str, Any]
    base_path: Path
    
    def get_asset_path(self, asset_name: str) -> Path:
        """Get path to a scene asset."""
        return self.base_path / "assets" / asset_name
    
    def get_narrative_path(self) -> Path:
        """Get path to scene narrative markdown."""
        narrative_path = self.base_path / "scene_narrative.md"
        if narrative_path.exists():
            return narrative_path
        return None
    
    def get_briefing_path(self) -> Path:
        """Get path to scene briefing markdown."""
        briefing_path = self.base_path / "scene_briefing.md"
        if briefing_path.exists():
            return briefing_path
        return None


class SceneLoader:
    """Loads and manages scene configurations."""
    
    def __init__(self, scenes_root: Optional[Path] = None):
        """
        Initialize scene loader.
        
        Args:
            scenes_root: Path to scenes/ folder (defaults to project_root/scenes)
        """
        if scenes_root is None:
            # Default to project_root/scenes
            project_root = Path(__file__).parent.parent
            scenes_root = project_root / "scenes"
        
        self.scenes_root = Path(scenes_root)
        self.registry = self._load_registry()
    
    def _load_registry(self) -> Dict[str, Any]:
        """Load scene registry."""
        registry_path = self.scenes_root / "scene_registry.yaml"
        
        if not registry_path.exists():
            raise FileNotFoundError(f"Scene registry not found: {registry_path}")
        
        with open(registry_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def list_scenes(self) -> Dict[str, Dict[str, Any]]:
        """List all available scenes."""
        return self.registry.get('scenes', {})
    
    def get_active_scene_id(self) -> str:
        """Get the ID of the currently active scene."""
        scenes = self.registry.get('scenes', {})
        
        # Find active scene
        for scene_id, scene_data in scenes.items():
            if scene_data.get('active', False):
                return scene_id
        
        # Fall back to default
        return self.registry.get('default_scene', 'scene1')
    
    def load_scene(self, scene_id: Optional[str] = None) -> SceneConfig:
        """
        Load a scene configuration.
        
        Args:
            scene_id: Scene identifier (defaults to active scene)
        
        Returns:
            SceneConfig object
        """
        if scene_id is None:
            scene_id = self.get_active_scene_id()
        
        # Get scene metadata from registry
        scenes = self.registry.get('scenes', {})
        if scene_id not in scenes:
            raise ValueError(f"Unknown scene_id: {scene_id}")
        
        scene_meta = scenes[scene_id]
        folder = scene_meta['folder']
        
        # Load scene config file
        scene_path = self.scenes_root / folder
        config_path = scene_path / "scene_config.yaml"
        
        if not config_path.exists():
            raise FileNotFoundError(f"Scene config not found: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        
        # Create SceneConfig object
        return SceneConfig(
            id=scene_id,
            name=scene_meta['name'],
            title=scene_meta['title'],
            folder=folder,
            timeframe=scene_meta['timeframe'],
            description=scene_meta['description'],
            active=scene_meta.get('active', False),
            config_data=config_data,
            base_path=scene_path
        )
    
    def get_scene_context(self, scene_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get scene context for agent prompts.
        
        Args:
            scene_id: Scene identifier (defaults to active scene)
        
        Returns:
            Dict with company snapshot, narrative, objectives
        """
        scene = self.load_scene(scene_id)
        config = scene.config_data
        
        # Extract key information
        company = config.get('company', {})
        scenes_data = config.get('scenes', {})
        scene_data = scenes_data.get('scene_1', {}) if scenes_data else {}
        
        return {
            'scene_id': scene.id,
            'scene_name': scene.name,
            'scene_title': scene.title,
            'timeframe': scene.timeframe,
            'company': company,
            'scene_objectives': scene_data.get('objectives', []),
            'scene_briefing': scene_data.get('briefing', {}),
            'success_criteria': scene_data.get('success_criteria', []),
            'config': config
        }


# Singleton instance
_scene_loader = None

def get_scene_loader(scenes_root: Optional[Path] = None) -> SceneLoader:
    """Get or create the scene loader singleton."""
    global _scene_loader
    if _scene_loader is None:
        _scene_loader = SceneLoader(scenes_root)
    return _scene_loader


# Test function
if __name__ == "__main__":
    print("Testing Scene Loader...")
    print()
    
    try:
        loader = get_scene_loader()
        print(f"✅ Scene loader initialized")
        print(f"   Scenes root: {loader.scenes_root}")
        print()
        
        # List scenes
        scenes = loader.list_scenes()
        print(f"📋 Available scenes: {len(scenes)}")
        for scene_id, scene_data in scenes.items():
            active = "✅ ACTIVE" if scene_data.get('active') else ""
            print(f"   - {scene_id}: {scene_data['name']} {active}")
        print()
        
        # Load active scene
        active_id = loader.get_active_scene_id()
        print(f"🎬 Loading active scene: {active_id}")
        scene = loader.load_scene()
        print(f"   ✅ Loaded: {scene.title}")
        print(f"   Timeframe: {scene.timeframe}")
        print(f"   Folder: {scene.folder}")
        print()
        
        # Get scene context
        context = loader.get_scene_context()
        print(f"📄 Scene context:")
        print(f"   Company: {context['company'].get('name')}")
        print(f"   Stage: {context['company'].get('stage')}")
        print(f"   Runway: {context['company'].get('key_metrics', {}).get('runway_months')} months")
        print(f"   Objectives: {len(context['scene_objectives'])}")
        print()
        
        print("🎉 All tests passed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

