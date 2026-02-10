---
name: generate-excel-report
description: >
  Generate a comprehensive Excel report from collected page speed data and save
  it locally. Creates a 4-sheet workbook with Summary, Core Web Vitals, Network
  Analysis, and Opportunities tabs.
---

# Generate Excel Report Skill

Generates a detailed Excel workbook from collected PageSpeed Insights and network
analysis data, saving it to the local `./output/` directory.

## When to Use

- After collecting ALL page speed data (PSI, CrUX, network waterfall)
- BEFORE writing the final markdown analysis report
- To provide clients with a downloadable data file

## Usage

### Generate from Collected Data

```bash
python {baseDir}/scripts/generate_excel.py \
  --data ./collected_data.json \
  --output-dir ./output
```

## Options

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| `--data` | Yes | - | Path to JSON file with collected data |
| `--output-dir` | No | `./output` | Directory to save the Excel file |
| `--job-id` | No | - | Optional prefix for the filename |

## Input Format

The `--data` JSON file should contain:

```json
{
  "urls": ["https://example.com", "https://example.com/page"],
  "psi_results": [
    {
      "url": "https://example.com",
      "strategies": {
        "mobile": {
          "performance_score": 65,
          "core_web_vitals": { ... },
          "field_metrics": { ... },
          "opportunities": [ ... ]
        },
        "desktop": { ... }
      }
    }
  ],
  "network_results": [
    {
      "url": "https://example.com",
      "total_requests": 45,
      "total_transfer_bytes": 1524000,
      "by_type": { ... },
      "largest_resources": [ ... ]
    }
  ]
}
```

## Output Format

```json
{
  "success": true,
  "file_path": "./output/page_speed_analysis_20260209_120000.xlsx",
  "filename": "page_speed_analysis_20260209_120000.xlsx",
  "sheets": ["Summary", "Core Web Vitals", "Network Analysis", "Opportunities"],
  "url_count": 5,
  "generated_at": "2026-02-09T12:00:00Z"
}
```

## Sheets Created

1. **Summary** - All URL scores at a glance (mobile/desktop scores, CWV status, top issue)
2. **Core Web Vitals** - Full metrics breakdown with lab and field data
3. **Network Analysis** - Resource details by type (scripts, images, CSS, fonts)
4. **Opportunities** - All PSI recommendations with estimated savings

## Error Handling

On failure, returns:
```json
{
  "success": false,
  "error": "Failed to generate Excel report: [details]"
}
```
