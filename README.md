# VIP PRO ULTIMATE AI — Web App

## File trong gói
| File | Vai trò |
|---|---|
| `app.py` | Web Flask chính (trang tool, BCR, MD5, widget con dự đoán) |
| `algorithms.py` | Thuật toán dự đoán TX + BCR (16 tín hiệu TX, 26 tín hiệu BCR, regime ensemble, MD5 analyzer) |
| `api_client.py` | Nối API lịch sử các tool + ảnh tool + link web |
| `database.py` | CSDL người dùng, key, nạp tiền |
| `ai_bot.py` | Bot ensemble tự học (RF+LSTM+XGBoost) — tùy chọn, không bắt buộc |
| `requirements.txt` | Thư viện Python |
| `run.py` | Chạy local |
| `render.yaml` | Deploy lên Render.com |

## Chạy local
```bash
pip install -r requirements.txt
python run.py
# hoặc: python app.py
```
Mở: http://localhost:5000

## Deploy Render.com
1. Push thư mục lên GitHub
2. Render → New Web Service → connect repo
3. Build: `pip install -r requirements.txt`
4. Start: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --threads 4`

## Tài khoản admin mặc định
Xem trong `database.py` (hàm khởi tạo) để lấy user admin đầu tiên.

## Lưu ý
- Tool cần kết nối API lịch sử (kwinstore) để có dữ liệu.
- `ai_bot.py` cần thêm: `pip install scikit-learn xgboost tensorflow pandas scipy joblib` (không bắt buộc cho web).
- Dự đoán chỉ mang tính tham khảo.
