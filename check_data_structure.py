import sys
sys.path.append('backend')

from backend.app.database.db import SyncSessionLocal
from backend.app.models.drivers_data import DriversData
import json

def check_data():
    # Get sync database session
    db = SyncSessionLocal()
    try:
        # Get first driver with additional_data
        result = db.query(DriversData).filter(DriversData.additional_data.isnot(None)).first()
        
        if result:
            print("Driver ID:", result.driver_id)
            print("Driver name:", result.name)
            print("Data type:", result.data_type)
            print("Has additional_data:", result.additional_data is not None)
            
            if result.additional_data:
                try:
                    data = json.loads(result.additional_data) if isinstance(result.additional_data, str) else result.additional_data
                    print("Additional data keys:", list(data.keys()))
                    
                    # Check for rides or similar data
                    for key, value in data.items():
                        print(f"\n--- {key} ---")
                        print(f"Type: {type(value)}")
                        if isinstance(value, list) and len(value) > 0:
                            print(f"List length: {len(value)}")
                            print(f"First item keys: {list(value[0].keys()) if isinstance(value[0], dict) else 'Not a dict'}")
                            if isinstance(value[0], dict):
                                print(f"First item sample: {json.dumps(value[0], indent=2)}")
                        elif isinstance(value, dict):
                            print(f"Dict keys: {list(value.keys())}")
                        else:
                            print(f"Value: {str(value)[:100]}...")
                            
                except Exception as e:
                    print("Error parsing additional_data:", e)
                    print("Raw additional_data (first 200 chars):", str(result.additional_data)[:200])
            else:
                print("No additional_data")
        else:
            print("No drivers with additional_data found")
            
    except Exception as e:
        print("Error:", e)
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_data()
