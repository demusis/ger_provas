
try:
    from services import exam_service
    print("Syntax OK")
except Exception as e:
    print(f"Syntax Error: {e}")
