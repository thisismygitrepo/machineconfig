#!/usr/bin/env python3
import tempfile
import shlex
from typing import Dict, List, Optional
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ZellijLayoutGenerator:
    def __init__(self, default_cwd: Optional[str] = None):
        self.default_cwd = default_cwd or "~"
        self.layout_template = """layout {
    default_tab_template {
        // the default zellij tab-bar and status bar plugins
        pane size=1 borderless=true {
            plugin location="zellij:compact-bar"
        }
        children
    }
"""
    
    def _parse_command(self, command: str) -> tuple[str, List[str]]:
        try:
            parts = shlex.split(command)
            if not parts: raise ValueError("Empty command provided")
            return parts[0], parts[1:] if len(parts) > 1 else []
        except ValueError as e:
            logger.error(f"Error parsing command '{command}': {e}")
            parts = command.split()
            return parts[0] if parts else "", parts[1:] if len(parts) > 1 else []
    
    def _format_args_for_kdl(self, args: List[str]) -> str:
        if not args: return ""
        formatted_args = []
        for arg in args:
            if ' ' in arg or '"' in arg or "'" in arg:
                escaped_arg = arg.replace('"', '\\"')
                formatted_args.append(f'"{escaped_arg}"')
            else:
                formatted_args.append(f'"{arg}"')
        return " ".join(formatted_args)
    
    def _create_tab_section(self, tab_name: str, command: str, cwd: Optional[str] = None) -> str:
        cmd, args = self._parse_command(command)
        args_str = self._format_args_for_kdl(args)
        tab_cwd = cwd or self.default_cwd
        escaped_tab_name = tab_name.replace('"', '\\"')
        tab_section = f'  tab name="{escaped_tab_name}" cwd="{tab_cwd}" {{\n'
        tab_section += f'    pane command="{cmd}" {{\n'
        if args_str: tab_section += f'      args {args_str}\n'
        tab_section += '    }\n  }\n'
        return tab_section
    
    def _validate_tab_config(self, tab_config: Dict[str, str]) -> None:
        if not tab_config: raise ValueError("Tab configuration cannot be empty")
        for tab_name, command in tab_config.items():
            if not tab_name.strip(): raise ValueError(f"Invalid tab name: {tab_name}")
            if not command.strip(): raise ValueError(f"Invalid command for tab '{tab_name}': {command}")
    
    def create_zellij_layout(self, tab_config: Dict[str, str], output_dir: Optional[str] = None) -> str:
        self._validate_tab_config(tab_config)
        logger.info(f"Creating Zellij layout with {len(tab_config)} tabs")
        layout_content = self.layout_template
        for tab_name, command in tab_config.items():
            layout_content += "\n" + self._create_tab_section(tab_name, command)
        layout_content += "\n}\n"
        try:
            if output_dir:
                output_path = Path(output_dir)
                output_path.mkdir(parents=True, exist_ok=True)
                layout_file = output_path / "zellij_layout.kdl"
                with open(layout_file, 'w', encoding='utf-8') as f:
                    f.write(layout_content)
                file_path = str(layout_file.absolute())
            else:
                with tempfile.NamedTemporaryFile(mode='w', suffix='.kdl', prefix='zellij_layout_', delete=False, encoding='utf-8') as f:
                    f.write(layout_content)
                    file_path = f.name
            logger.info(f"Zellij layout file created: {file_path}")
            return file_path
        except OSError as e:
            logger.error(f"Failed to create layout file: {e}")
            raise
    
    def create_layout_from_config_file(self, config_file: str, output_dir: Optional[str] = None) -> str:
        tab_config = {}
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith('#'): continue
                    if '|' not in line:
                        logger.warning(f"Skipping invalid line {line_num}: {line}")
                        continue
                    tab_name, command = line.split('|', 1)
                    tab_config[tab_name.strip()] = command.strip()
            return self.create_zellij_layout(tab_config, output_dir)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {config_file}")
        except Exception as e:
            raise ValueError(f"Error reading configuration file: {e}")
    
    def get_layout_preview(self, tab_config: Dict[str, str]) -> str:
        self._validate_tab_config(tab_config)
        layout_content = self.layout_template
        for tab_name, command in tab_config.items():
            layout_content += "\n" + self._create_tab_section(tab_name, command)
        return layout_content + "\n}\n"


def created_zellij_layout(tab_config: Dict[str, str], output_dir: Optional[str] = None, default_cwd: Optional[str] = None) -> str:
    generator = ZellijLayoutGenerator(default_cwd=default_cwd)
    return generator.create_zellij_layout(tab_config, output_dir)

if __name__ == "__main__":
    sample_tabs = {
        "🤖Bot1": "~/scripts/fire -mO go1.py bot1 --kw create_new_bot True",
        "🤖Bot2": "~/scripts/fire -mO go2.py bot2 --kw create_new_bot True", 
        "📊Monitor": "htop",
        "📝Logs": "tail -f /var/log/app.log"
    }
    try:
        layout_path = created_zellij_layout(sample_tabs)
        print(f"✅ Layout created successfully: {layout_path}")
        generator = ZellijLayoutGenerator()
        preview = generator.get_layout_preview(sample_tabs)
        print("\n📋 Layout Preview:")
        print(preview)
    except Exception as e:
        print(f"❌ Error: {e}")
