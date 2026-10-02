# شرکت دلتا - مرحله ۱

    python -m venv venv
    source venv/bin/activate      # ویندوز: venv\Scripts\activate
    pip install -r requirements.txt
    python -m scripts.create_admin
    uvicorn app.main:app --reload

سپس http://127.0.0.1:8000 را باز کنید.
