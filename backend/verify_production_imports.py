import sys
import os

# Simulate production: run from parent of 'backend'
backend_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(backend_dir)
sys.path.append(parent_dir)

print(f"Parent directory: {parent_dir}")
print(f"Backend directory: {backend_dir}")

try:
    print("Testing 'from backend.main import app'...")
    from backend.main import app
    print("SUCCESS: main.app imported")

    print("Testing 'from backend.services.recommendation_service import recommendation_service'...")
    from backend.services.recommendation_service import recommendation_service
    print("SUCCESS: recommendation_service imported")

    print("Testing 'from backend.api.routes.stocks import router'...")
    from backend.api.routes.stocks import router
    print("SUCCESS: stocks router imported")

    print("\n[ALL PRODUCTION IMPORTS VERIFIED]")

except Exception as e:
    print(f"\n[IMPORT ERROR]: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
