#!/usr/bin/env python3

# Simple test to check basic Python functionality
print("🚀 Starting basic test...")

try:
    import pandas as pd
    print("✅ pandas imported successfully")
    
    import json
    print("✅ json imported successfully")
    
    import uuid
    print("✅ uuid imported successfully")
    
    from pathlib import Path
    print("✅ pathlib imported successfully")
    
    # Test directory creation
    test_dir = Path.home() / "tmp_results" / "test_dir"
    test_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ Directory created: {test_dir}")
    
    # Test JSON serialization
    test_data = {"test": "data", "number": 42}
    test_file = test_dir / "test.json"
    with open(test_file, 'w') as f:
        json.dump(test_data, f)
    print("✅ JSON file written")
    
    # Test JSON deserialization
    with open(test_file, 'r') as f:
        loaded_data = json.load(f)
    print(f"✅ JSON file loaded: {loaded_data}")
    
    # Clean up
    test_file.unlink()
    test_dir.rmdir()
    print("✅ Cleanup completed")
    
    print("🎉 All basic tests passed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
