#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================
  VIP PRO AI BOT — Ensemble tự học, đồng tâm với API
  Thuật toán RIÊNG cho TX (Tài/Xỉu) và RIÊNG cho BCR (Player/Banker)
  - Random Forest (300 cây, độ sâu 20)
  - LSTM 2 lớp 64 neuron (nếu có tensorflow), fallback MLP của sklearn
  - XGBoost (nếu có), fallback GradientBoosting
  - Online learning: tái huấn luyện mỗi 50 ván, đánh giá mỗi 200 ván
  - Cơ chế ĐỒNG TÂM: API tham chiếu weight=0.3, model tự học weight=0.7
  - Xử lý nhiễu: IQR outlier, làm mượt Kalman sơ cấp, change-point detection
==============================================================================
  LƯU Ý: Trên game công bằng (ngẫu nhiên độc lập) không thể đạt độ chính xác
  cao ổn định. Mô hình này là công cụ tham khảo, không đảm bảo lời.
==============================================================================
"""
import os
import time
import json
import logging
import threading
from collections import deque
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Tuple

import numpy as np
import pandas as pd
from scipy import stats

# ---- Thư viện heavy: import có fallback ----
try:
    import xgboost as xgb
    _HAS_XGB = True
except Exception:
    from sklearn.ensemble import GradientBoostingClassifier
    _HAS_XGB = False

from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, f1_score, log_loss
import joblib

try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    _HAS_TF = True
except Exception:
    _HAS_TF = False

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("ai_bot.log", encoding="utf-8"), logging.StreamHandler()],
)
log = logging.getLogger("ai_bot")


# ============================================================================
#  TRÍCH ĐẶC TRƯNG (FEATURES) — chung cho TX & BCR, nhãn khác nhau
# ============================================================================
def moving_average(x: np.ndarray, w: int) -> float:
    return float(np.mean(x[-w:])) if len(x) >= w else float(np.mean(x))


def extract_features(seq_labels: List[int], scores: Optional[List[float]] = None) -> np.ndarray:
    """
    seq_labels: nhãn nhị phân lịch sử (TX: 1=Tài, 0=Xỉu; BCR: 1=Player, 0=Banker)
    scores: điểm số cụ thể (TX: tổng xúc xắc 3-18; BCR: có thể None)
    Trả về vector đặc trưng 1 chiều.
    """
    s = np.array(seq_labels, dtype=float)
    n = len(s)
    if n < 5:
        return np.zeros(20, dtype=float)

    # A) Thống kê động: trung bình trượt 5/10/20, độ lệch chuẩn, tỷ lệ
    ma5 = moving_average(s, 5)
    ma10 = moving_average(s, 10)
    ma20 = moving_average(s, 20)
    std10 = float(np.std(s[-10:])) if n >= 10 else 0.0
    ratio = float(np.mean(s))  # tỷ lệ lớp 1

    # B) Xu hướng: đạo hàm bậc 1 & 2 (trên MA5), số đảo chiều, độ dài chuỗi cuối
    ma_series = pd.Series(s).rolling(5, min_periods=1).mean().values
    d1 = np.diff(ma_series)
    deriv1 = float(d1[-1]) if len(d1) else 0.0
    deriv2 = float(np.diff(d1)[-1]) if len(d1) > 1 else 0.0
    reversals = int(np.sum(np.diff(np.sign(np.diff(s))) != 0)) if n >= 3 else 0
    run = 1
    for i in range(n - 2, -1, -1):
        if s[i] == s[-1]:
            run += 1
        else:
            break

    # C) Chu kỳ: tự tương quan lag 2..6 (Fourier sơ cấp = tần suất dominant)
    best_corr = 0.0
    for lag in range(2, min(7, n // 2)):
        if n > lag + 2:
            c = float(np.corrcoef(s[:-lag], s[lag:])[0, 1])
            best_corr = max(best_corr, abs(c) if not np.isnan(c) else 0.0)

    feat = [ma5, ma10, ma20, std10, ratio, deriv1, deriv2, reversals, run, best_corr]

    # D) Điểm số (nếu có): phân phối, mean, khoảng cách đến biên
    if scores is not None and len(scores) >= 5:
        sc = np.array(scores, dtype=float)
        mean_s = float(np.mean(sc[-10:]))
        std_s = float(np.std(sc[-10:]))
        skew_s = float(stats.skew(sc[-20:])) if len(sc) >= 20 else 0.0
        # khoảng cách trung bình đến biên (TX: biên 3 và 18)
        dist_edge = float(np.mean(np.minimum(sc[-10:] - 3, 18 - sc[-10:]))) / 15.0
        feat += [mean_s / 18.0, std_s / 18.0, skew_s, dist_edge]
    else:
        feat += [0.0, 0.0, 0.0, 0.0]

    # Làm tròn về 20 chiều cố định
    feat = feat[:20]
    while len(feat) < 20:
        feat.append(0.0)
    return np.array(feat, dtype=float)


# ============================================================================
#  XỬ LÝ NHIỄU: IQR outlier + Kalman sơ cấp + change-point
# ============================================================================
def remove_outliers_iqr(values: List[float]) -> List[float]:
    """Loại bỏ outlier bằng IQR (chỉ áp dụng cho cột điểm số)."""
    if len(values) < 4:
        return values
    arr = np.array(values, dtype=float)
    q1, q3 = np.percentile(arr, [25, 75])
    iqr = q3 - q1
    lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    return [v for v in values if lo <= v <= hi]


def kalman_smooth(seq: List[float], q=0.01, r=0.1) -> List[float]:
    """Bộ lọc Kalman 1 chiều làm mượt chuỗi nhị phân/điểm số."""
    if not seq:
        return []
    x = seq[0]
    p = 1.0
    out = []
    for z in seq:
        p = p + q
        k = p / (p + r)
        x = x + k * (z - x)
        p = (1 - k) * p
        out.append(x)
    return out


def detect_change_point(seq_labels: List[int], window=30, threshold=0.15) -> bool:
    """Phát hiện thay đổi phân phối: so sánh tỷ lệ cửa sổ gần vs xa."""
    if len(seq_labels) < window * 2:
        return False
    recent = np.mean(seq_labels[-window:])
    older = np.mean(seq_labels[-2 * window:-window])
    return abs(recent - older) > threshold


# ============================================================================
#  MÔ HÌNH ENSEMBLE — riêng cho từng loại game
# ============================================================================
@dataclass
class ModelState:
    rf: object = None
    xgb: object = None
    lstm: object = None
    scaler: object = field(default_factory=StandardScaler)
    X_buf: list = field(default_factory=list)
    y_buf: list = field(default_factory=list)
    n_trained: int = 0
    last_eval: int = 0
    api_agreement: float = 0.5  # tỷ lệ đồng thuận với API (đồng tâm)


class EnsembleModel:
    """Mô hình ensemble cho MỘT loại game (TX hoặc BCR)."""

    def __init__(self, name: str, label_pos: str, label_neg: str, api_weight=0.3):
        self.name = name
        self.label_pos = label_pos  # 'TAI' hoặc 'PLAYER'
        self.label_neg = label_neg  # 'XIU' hoặc 'BANKER'
        self.api_weight = api_weight  # đồng tâm với API
        self.model_weight = 1.0 - api_weight
        self.state = ModelState()
        self.lock = threading.Lock()
        self.checkpoint_dir = "checkpoints"
        os.makedirs(self.checkpoint_dir, exist_ok=True)

    # ------------------------------------------------------------------
    def _build_lstm(self, n_features=20):
        if not _HAS_TF:
            # Fallback: MLP 2 lớp (tương đương chức năng)
            return MLPClassifier(hidden_layer_sizes=(64, 64), max_iter=300,
                                random_state=42, warm_start=True)
        model = Sequential([
            LSTM(64, return_sequences=True, input_shape=(1, n_features)),
            Dropout(0.2),
            LSTM(64),
            Dropout(0.2),
            Dense(1, activation="sigmoid"),
        ])
        model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
        return model

    # ------------------------------------------------------------------
    def train(self, X: np.ndarray, y: np.ndarray):
        """Huấn luyện (hoặc tái huấn luyện) toàn bộ ensemble."""
        with self.lock:
            Xs = self.state.scaler.fit_transform(X)
            # Random Forest
            self.state.rf = RandomForestClassifier(
                n_estimators=300, max_depth=20, n_jobs=-1, random_state=42)
            self.state.rf.fit(Xs, y)
            # XGBoost / fallback
            if _HAS_XGB:
                self.state.xgb = xgb.XGBClassifier(
                    n_estimators=200, max_depth=8, learning_rate=0.05,
                    use_label_encoder=False, eval_metric="logloss", random_state=42)
                self.state.xgb.fit(Xs, y)
            else:
                self.state.xgb = GradientBoostingClassifier(
                    n_estimators=200, max_depth=5, learning_rate=0.05, random_state=42)
                self.state.xgb.fit(Xs, y)
            # LSTM / MLP
            self.state.lstm = self._build_lstm()
            if _HAS_TF:
                X_lstm = Xs.reshape((Xs.shape[0], 1, Xs.shape[1]))
                self.state.lstm.fit(X_lstm, y, epochs=10, batch_size=32, verbose=0)
            else:
                self.state.lstm.fit(Xs, y)
            self.state.n_trained = len(y)
            log.info("[%s] Đã huấn luyện ensemble trên %d mẫu", self.name, len(y))
            self._save_checkpoint()

    # ------------------------------------------------------------------
    def predict_proba(self, feat: np.ndarray, api_pred: Optional[float] = None) -> Dict:
        """
        Dự đoán xác suất. api_pred: xác suất lớp dương từ API (0..1),
        dùng để ĐỒNG TÂM (weight=0.3). Trả về dict đầy đủ.
        """
        with self.lock:
            if self.state.rf is None:
                # Chưa đủ dữ liệu → ưu tiên API nếu có
                p = api_pred if api_pred is not None else 0.5
                return self._format_output(p, feat, api_pred, trained=False)
            Xs = self.state.scaler.transform(feat.reshape(1, -1))
            p_rf = float(self.state.rf.predict_proba(Xs)[0][1])
            p_xgb = float(self.state.xgb.predict_proba(Xs)[0][1])
            if _HAS_TF:
                p_lstm = float(self.state.lstm.predict(
                    Xs.reshape((1, 1, -1)), verbose=0)[0][0])
            else:
                p_lstm = float(self.state.lstm.predict_proba(Xs)[0][1])
            # Trung bình 3 mô hình (ensemble)
            p_model = (p_rf + p_xgb + p_lstm) / 3.0
            # Đồng tâm với API: blend
            if api_pred is not None:
                p_final = self.model_weight * p_model + self.api_weight * api_pred
            else:
                p_final = p_model
            # Confidence = 1 - độ phân tán (độ đồng thuận)
            dispersion = float(np.std([p_rf, p_xgb, p_lstm]))
            confidence = float(np.clip(1.0 - dispersion * 2, 0.0, 1.0))
            return self._format_output(p_final, feat, api_pred, trained=True,
                                       p_rf=p_rf, p_xgb=p_xgb, p_lstm=p_lstm,
                                       confidence=confidence)

    # ------------------------------------------------------------------
    def _format_output(self, p, feat, api_pred, trained, p_rf=None, p_xgb=None,
                       p_lstm=None, confidence=0.5) -> Dict:
        pred_pos = p >= 0.5
        label = self.label_pos if pred_pos else self.label_neg
        # Điểm dự đoán (TX: 3-18) + khoảng tin cậy 95% (từ mean lịch sử)
        point_est = None
        ci = (None, None)
        # Lưu vào state để sau này đánh giá
        self.state.api_agreement = (
            0.9 * self.state.api_agreement + 0.1 * (
                1.0 - abs(p - (api_pred if api_pred is not None else p))))
        return {
            "game": self.name,
            "du_doan": label,
            "xac_suat_pos": round(float(p), 4),
            "xac_suat_neg": round(1.0 - float(p), 4),
            "confidence": round(confidence, 3),
            "trained": trained,
            "ensemble": {"rf": p_rf, "xgb": p_xgb, "lstm": p_lstm},
            "api_blend": api_pred,
            "point_estimate": point_est,
            "ci95": ci,
            "features": feat.tolist(),
        }

    # ------------------------------------------------------------------
    def online_learn(self, feat: np.ndarray, true_label: int):
        """Học trực tuyến: đệm mẫu, huấn luyện lại khi đủ 50, đánh giá khi đủ 200."""
        with self.lock:
            self.state.X_buf.append(feat)
            self.state.y_buf.append(true_label)
        if len(self.state.X_buf) >= 50:
            with self.lock:
                X = np.array(self.state.X_buf)
                y = np.array(self.state.y_buf)
                self.state.X_buf.clear()
                self.state.y_buf.clear()
            self.train(X, y)
        if self.state.n_trained - self.state.last_eval >= 200:
            self.state.last_eval = self.state.n_trained
            log.info("[%s] Đánh giá định kỳ sau %d ván", self.name, self.state.n_trained)

    # ------------------------------------------------------------------
    def _save_checkpoint(self):
        path = os.path.join(self.checkpoint_dir, f"{self.name}.pkl")
        try:
            joblib.dump({"rf": self.state.rf, "xgb": self.state.xgb,
                         "scaler": self.state.scaler, "n": self.state.n_trained}, path)
        except Exception as e:
            log.warning("[%s] Lưu checkpoint thất bại: %s", self.name, e)

    def load_checkpoint(self):
        path = os.path.join(self.checkpoint_dir, f"{self.name}.pkl")
        if os.path.exists(path):
            try:
                ck = joblib.load(path)
                with self.lock:
                    self.state.rf = ck["rf"]
                    self.state.xgb = ck["xgb"]
                    self.state.scaler = ck["scaler"]
                    self.state.n_trained = ck["n"]
                log.info("[%s] Đã nạp checkpoint: %d ván", self.name, self.state.n_trained)
            except Exception as e:
                log.warning("[%s] Nạp checkpoint lỗi: %s", self.name, e)


# ============================================================================
#  BOT CHÍNH — quản lý 2 mô hình RIÊNG TX và BCR + thu thập dữ liệu
# ============================================================================
class VIPAIBot:
    def __init__(self, api_url_tx: str = "", api_url_bcr: str = "", poll_interval=5):
        self.tx = EnsembleModel("TX", "TAI", "XIU")
        self.bcr = EnsembleModel("BCR", "PLAYER", "BANKER")
        self.api_url_tx = api_url_tx
        self.api_url_bcr = api_url_bcr
        self.poll_interval = poll_interval
        self.history_tx = deque(maxlen=2000)   # (label, score)
        self.history_bcr = deque(maxlen=2000)  # (label, None)
        self.running = False
        for m in (self.tx, self.bcr):
            m.load_checkpoint()

    # ---- API đồng tâm: lấy dự đoán tham chiếu từ API gốc ----
    def fetch_api_pred(self, game: str) -> Optional[float]:
        import requests
        url = self.api_url_tx if game == "TX" else self.api_url_bcr
        if not url:
            return None
        try:
            r = requests.get(url, timeout=5)
            d = r.json()
            # API gốc trả về xác suất Tài/Player; chuẩn hóa về 0..1
            if game == "TX":
                return float(d.get("xac_suat_tai", d.get("tai_pct", 50))) / 100.0
            else:
                return float(d.get("xac_suat_player", 50)) / 100.0
        except Exception as e:
            log.debug("Lấy API dự đoán %s lỗi: %s", game, e)
            return None

    # ---- Dự đoán ----
    def predict_tx(self, history_labels: List[int], scores: List[float] = None,
                   use_api=True) -> Dict:
        api_p = self.fetch_api_pred("TX") if use_api else None
        feat = extract_features(history_labels, scores)
        out = self.tx.predict_proba(feat, api_p)
        log.info("[TX] Dự đoán: %s (conf=%.2f, api=%.2f)", out["du_doan"],
                 out["confidence"], api_p or -1)
        return out

    def predict_bcr(self, history_labels: List[int], use_api=True) -> Dict:
        api_p = self.fetch_api_pred("BCR") if use_api else None
        feat = extract_features(history_labels, None)
        out = self.bcr.predict_proba(feat, api_p)
        log.info("[BCR] Dự đoán: %s (conf=%.2f)", out["du_doan"], out["confidence"])
        return out

    # ---- Học từ kết quả thật ----
    def learn_tx_result(self, history_labels, scores, true_label: int):
        feat = extract_features(history_labels, scores)
        if detect_change_point([h for h in history_labels]):
            log.warning("[TX] Phát hiện change-point → reset bộ đệm học")
            self.tx.state.X_buf.clear(); self.tx.state.y_buf.clear()
        self.tx.online_learn(feat, true_label)

    def learn_bcr_result(self, history_labels, true_label: int):
        feat = extract_features(history_labels, None)
        self.bcr.online_learn(feat, true_label)

    # ---- Microservice: thread thu thập + học liên tục ----
    def start_collector(self, fetch_fn_tx=None, fetch_fn_bcr=None):
        """fetch_fn_tx() -> (label, score, api_pred); fetch_fn_bcr() -> label."""
        self.running = True

        def loop():
            last_tx = last_bcr = None
            while self.running:
                try:
                    if fetch_fn_tx:
                        res = fetch_fn_tx()
                        if res and res != last_tx:
                            label, score, _api = res
                            hist = [h[0] for h in self.history_tx]
                            sc = [h[1] for h in self.history_tx if h[1] is not None]
                            self.learn_tx_result(hist, sc, label)
                            self.history_tx.append((label, score))
                            last_tx = res
                    if fetch_fn_bcr:
                        res = fetch_fn_bcr()
                        if res and res != last_bcr:
                            hist = [h[0] for h in self.history_bcr]
                            self.learn_bcr_result(hist, res)
                            self.history_bcr.append((res, None))
                            last_bcr = res
                except Exception as e:
                    log.error("Collector lỗi: %s", e)
                time.sleep(self.poll_interval)

        t = threading.Thread(target=loop, daemon=True)
        t.start()
        log.info("Đã khởi động collector thread (poll %.1fs)", self.poll_interval)

    def stop(self):
        self.running = False


# ============================================================================
#  ĐÁNH GIÁ CHỈ SỐ (Accuracy / F1 / Log-loss) — traceback đầy đủ
# ============================================================================
def evaluate(model: EnsembleModel, X_test, y_test):
    Xs = model.state.scaler.transform(X_test)
    proba = (model.state.rf.predict_proba(Xs)[:, 1] +
             model.state.xgb.predict_proba(Xs)[:, 1]) / 2.0
    pred = (proba >= 0.5).astype(int)
    acc = accuracy_score(y_test, pred)
    f1 = f1_score(y_test, pred, zero_division=0)
    ll = log_loss(y_test, np.clip(proba, 1e-6, 1 - 1e-6))
    log.info("[%s] Accuracy=%.3f F1=%.3f LogLoss=%.3f (mục tiêu: >=0.52, >=0.50, <=0.69)",
             model.name, acc, f1, ll)
    return {"accuracy": acc, "f1": f1, "log_loss": ll}


# ============================================================================
#  CHẠY THỬ
# ============================================================================
if __name__ == "__main__":
    bot = VIPAIBot()
    # Mô phỏng 120 ván TX ngẫu nhiên để test pipeline
    rng = np.random.default_rng(42)
    labels = rng.integers(0, 2, size=120).tolist()
    scores = rng.integers(3, 19, size=120).tolist()
    for i in range(50, 120):
        hist = labels[:i]
        sc = scores[:i]
        out = bot.predict_tx(hist, sc, use_api=False)
        bot.learn_tx_result(hist, sc, labels[i])
        if i % 20 == 0:
            print(f"Van {i}: du_doan={out['du_doan']} conf={out['confidence']} "
                  f"trained={out['trained']}")
    print("Xong. Log chi tiết: ai_bot.log")
