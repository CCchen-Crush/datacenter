#!/usr/bin/env python3
"""Derive the compact input files used by the MATLAB experiments.

Sources (download first, see data_prep/README.md):
  * Alibaba PAI GPU trace v2020 (Weng et al., NSDI'22): pai_task_table.csv
  * Azure LLM inference trace 2024 (Stojkovic et al., HPCA'25, CC-BY 4.0):
      AzureLLMInferenceTrace_code_1week.csv, AzureLLMInferenceTrace_conv_1week.csv
  * Open-Meteo ERA5 archive (CC-BY 4.0), Suzhou-Wujiang, 2024-06-15..2024-08-31

Outputs (written to ../data):
  pai_gpu_occupancy_15min.csv      busy GPUs per 15 min, by runtime class, stable days 7..64
  azure_llm_tokens_15min_local.csv tokens per 15 min, per service, local time (UTC-4)
  weather_suzhou_2024summer.csv    hourly temperature / GHI / RH (Asia/Shanghai)

Usage:
  python3 prepare_data.py --pai DIR --azure DIR --weather FILE --out ../data
"""
import argparse, os
import numpy as np
import pandas as pd

LOCAL_OFFSET_PAI = 8 * 3600      # PAI timestamps keep time-of-day in UTC+8 (trace README)
AZURE_LOCAL_SHIFT = "-4h"        # assumption: request volume dominated by US-Eastern business hours
CLASS_EDGES_H = (1.0, 12.0)      # runtime <=1 h -> C1, 1-12 h -> C2, >12 h -> C3
STABLE_DAYS = range(7, 65)       # drop warm-up / tail days of the trace


def pai_profile(pai_dir):
    cols = ["job_name", "task_name", "inst_num", "status", "start_time", "end_time",
            "plan_cpu", "plan_mem", "plan_gpu", "gpu_type"]
    t = pd.read_csv(os.path.join(pai_dir, "pai_task_table.csv"), header=None, names=cols)
    t = t[(t.status == "Terminated") & (t.plan_gpu > 0)].dropna(subset=["start_time", "end_time"])
    t = t[t.end_time > t.start_time].copy()
    t["gpus"] = t.inst_num * t.plan_gpu / 100.0
    dur_h = (t.end_time - t.start_time) / 3600.0
    t["cls"] = np.where(dur_h <= CLASS_EDGES_H[0], 1, np.where(dur_h <= CLASS_EDGES_H[1], 2, 3))
    t0 = (t.start_time.min() + LOCAL_OFFSET_PAI) // 86400 * 86400 - LOCAL_OFFSET_PAI
    res = 60
    nb = int((t.end_time.max() - t0) // res) + 2
    occ = np.zeros((3, nb))
    for c in (1, 2, 3):
        s = t[t.cls == c]
        a = ((s.start_time - t0) // res).astype(int).values
        b = ((s.end_time - t0) // res).astype(int).values
        diff = np.zeros(nb + 1)
        np.add.at(diff, a, s.gpus.values)
        np.add.at(diff, b, -s.gpus.values)
        occ[c - 1] = np.cumsum(diff)[:nb]
    n15 = nb // 15
    occ15 = occ[:, :n15 * 15].reshape(3, n15, 15).mean(axis=2)
    ndays = n15 // 96
    day = occ15[:, :ndays * 96].reshape(3, ndays, 96)
    unix_day0 = int((t0 + LOCAL_OFFSET_PAI) // 86400)
    rows = []
    for k in STABLE_DAYS:
        dow = (unix_day0 + k + 3) % 7          # 0 = Monday (1970-01-01 was a Thursday)
        for s in range(96):
            rows.append((k, dow, s, day[0, k, s], day[1, k, s], day[2, k, s]))
    return pd.DataFrame(rows, columns=["day", "dow", "slot", "gpus_c1", "gpus_c2", "gpus_c3"])


def azure_profile(azure_dir):
    frames = []
    for svc in ("code", "conv"):
        acc = None
        path = os.path.join(azure_dir, f"AzureLLMInferenceTrace_{svc}_1week.csv")
        for ch in pd.read_csv(path, chunksize=4_000_000):
            ts = pd.to_datetime(ch.TIMESTAMP.str.slice(0, 19), format="%Y-%m-%d %H:%M:%S")
            loc = (ts + pd.Timedelta(AZURE_LOCAL_SHIFT)).dt.floor("15min")
            g = pd.DataFrame({"t": loc, "requests": 1, "ctx_tokens": ch.ContextTokens,
                              "gen_tokens": ch.GeneratedTokens}).groupby("t").sum()
            acc = g if acc is None else acc.add(g, fill_value=0)
        acc = acc.sort_index()
        acc["service"] = svc
        frames.append(acc.reset_index())
    out = pd.concat(frames)
    out["date"] = out.t.dt.strftime("%Y-%m-%d")
    out["slot"] = out.t.dt.hour * 4 + out.t.dt.minute // 15
    full = out.groupby(["service", "date"]).slot.transform("count") == 96   # keep full local days
    out = out[full]
    return out[["service", "date", "slot", "requests", "ctx_tokens", "gen_tokens"]]


def weather(file):
    w = pd.read_csv(file, skiprows=3)
    w.columns = ["time", "temp_c", "ghi_wm2", "rh_pct"]
    return w


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pai", required=True)
    ap.add_argument("--azure", required=True)
    ap.add_argument("--weather", required=True)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "data"))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    pai_profile(a.pai).to_csv(os.path.join(a.out, "pai_gpu_occupancy_15min.csv"), index=False, float_format="%.2f")
    azure_profile(a.azure).to_csv(os.path.join(a.out, "azure_llm_tokens_15min_local.csv"), index=False)
    weather(a.weather).to_csv(os.path.join(a.out, "weather_suzhou_2024summer.csv"), index=False)
    print("done")
