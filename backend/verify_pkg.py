import sys
import os

# Simulate running from repo root by adding parent of 'backend' to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

try:
    from backend.main import app
    print("IMPORT_OK")

    from backend.services.recommendation_service import recommendation_service
    print("RECOMMENDATION_IMPORT_OK")

except Exception as e:
    print(f"IMPORT_FAIL: {e}")
    import traceback
    traceback.print_exc()
