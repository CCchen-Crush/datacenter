# Data preparation

The MATLAB experiments read three small derived files in `data/` (already committed).
This folder documents how they were produced from public sources, so they can be rebuilt.

| Derived file | Source | Licence / citation |
|---|---|---|
| `data/pai_gpu_occupancy_15min.csv` | Alibaba PAI GPU cluster trace v2020, `pai_task_table` ([alibaba/clusterdata](https://github.com/alibaba/clusterdata/tree/master/cluster-trace-gpu-v2020)) | cite Weng et al., *MLaaS in the Wild*, NSDI 2022 |
| `data/azure_llm_tokens_15min_local.csv` | Azure LLM inference trace 2024 (code + conversation, 1 week) ([Azure/AzurePublicDataset](https://github.com/Azure/AzurePublicDataset/blob/master/AzureLLMInferenceDataset2024.md)) | CC-BY 4.0; cite Stojkovic et al., *DynamoLLM*, HPCA 2025 |
| `data/weather_suzhou_2024summer.csv` | Open-Meteo historical weather API (ERA5 reanalysis), 31.16 N 120.64 E, 2024-06-15..2024-08-31 | CC-BY 4.0 (Open-Meteo / Copernicus ERA5) |

## Rebuild

```bash
# 1. PAI trace (about 95 MB compressed); checksums are listed in the trace README
mkdir -p raw/pai && cd raw/pai
curl -O https://aliopentrace.oss-cn-beijing.aliyuncs.com/v2020GPUTraces/pai_task_table.tar.gz
tar -xzf pai_task_table.tar.gz && cd ../..
# 2. Azure LLM inference trace 2024 (about 1.8 GB)
mkdir -p raw/azure && cd raw/azure
for f in code conv; do curl -LO https://github.com/Azure/AzurePublicDataset/releases/download/dataset-llm-2024/AzureLLMInferenceTrace_${f}_1week.csv; done; cd ../..
# 3. Weather
curl -o raw/weather.csv "https://archive-api.open-meteo.com/v1/archive?latitude=31.16&longitude=120.64&start_date=2024-06-15&end_date=2024-08-31&hourly=temperature_2m,shortwave_radiation,relative_humidity_2m&timezone=Asia%2FShanghai&format=csv"
# 4. Derive
pip install numpy pandas
python3 prepare_data.py --pai raw/pai --azure raw/azure --weather raw/weather.csv --out ../data
```

## Processing choices

* **PAI**: only `Terminated` tasks with `plan_gpu > 0`. Busy GPUs = `inst_num * plan_gpu / 100`, spread
  uniformly over `[start_time, end_time]` at 1-min resolution, averaged to 15 min. Time of day uses
  UTC+8 (the trace keeps the original time of day in that zone). Tasks are split by runtime into
  C1 (<= 1 h), C2 (1-12 h), C3 (> 12 h). Days 7-64 are kept (the first and last days of the trace are
  truncated). Shares of GPU-hours: C1 6.6 %, C2 43.9 %, C3 49.5 %.
* **Azure LLM**: requests aggregated to 15 min; load index = context + generated tokens, normalised per
  service. The trace is in UTC and peaks at 13-21 UTC (US business hours), so it is shifted to UTC-4 and
  its *local-time shape* is used for the data centre's inference demand (stated as an assumption).
* **Weather**: hourly 2 m temperature and GHI; GHI is the mean of the preceding hour and is centred on
  the half hour before interpolation to 15 min. PV power uses a PVWatts-v5-type model.
