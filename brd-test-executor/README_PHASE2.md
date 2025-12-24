# 🚀 BRD Test Executor - Phase 2

Tự động chạy test cases từ Google Sheet sử dụng Playwright.

## 📋 Prerequisites

- Python 3.9+
- Google Service Account credentials
- Azure OpenAI API key
- Test account cho website

## 🛠️ Setup

1. **Install dependencies:**
```bash
   pip install -r requirements.txt
   playwright install chromium
```

2. **Copy .env.example → .env và điền thông tin**

3. **Copy service account credentials vào credentials/**

## 🎯 Usage
```bash
# Run test executor
python run_executor.py --sheet-name "BRD_Portal_20251023" --browser chromium
```

## 📂 Project Structure

- `app/automation/` - Test generation & execution core
- `tests/generated/` - Auto-generated test files
- `screenshots/` - Failed test screenshots
- `logs/` - Execution logs

## 🔗 Integration với Phase 1

Phase 1 (Generator) → Google Sheet → Phase 2 (Executor)
