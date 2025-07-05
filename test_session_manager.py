#!/usr/bin/env python3

import sys
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

try:
    from machineconfig.cluster.sessions_managers.zellij_remote_manager import ZellijSessionManager
    
    print("✅ Successfully imported ZellijSessionManager")
    
    # Test basic functionality
    machine2zellij_tabs = {
        "test_server": {
            "monitor": ("echo 'test monitor'", "/tmp"),
            "status": ("echo 'test status'", "/tmp")
        }
    }
    
    print("🔧 Testing session creation...")
    manager = ZellijSessionManager(
        machine2zellij_tabs=machine2zellij_tabs,
        session_name_prefix="Test"
    )
    print(f"📊 Created manager with {len(manager.managers)} remote managers")
    
    print("💾 Testing save functionality...")
    session_id = manager.save()
    print(f"✅ Session saved with ID: {session_id}")
    
    print("📋 Listing saved sessions...")
    saved_sessions = ZellijSessionManager.list_saved_sessions()
    print(f"Available sessions: {saved_sessions}")
    
    print(f"📂 Testing load functionality...")
    loaded_manager = ZellijSessionManager.load(session_id)
    print(f"✅ Loaded manager with {len(loaded_manager.managers)} remote managers")
    
    print("🗑️ Cleaning up...")
    ZellijSessionManager.delete_session(session_id)
    print("✅ Test completed successfully!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
