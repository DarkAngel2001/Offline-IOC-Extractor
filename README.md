# IOC Extractor

`ioc-extractor` is a deterministic, offline command-line utility designed for defensive security analysis. It parses text-based artifacts, extracts candidate indicators of compromise (IOCs), validates them structurally, normalizes/refangs them where configured, applies conservative context scoring and warning lists, and exports clean results to JSON and CSV formats.

---

## Features & Functionality

- **Artifact Readers:** Supports parsing plain text (`.txt`), system/security logs (`.log`), and raw RFC 822 MIME emails (`.eml` headers and plain-text body parts only).
- **Indicator Types:** Extracts and structurally validates:
  - IPv4 addresses (excluding IPv6)
  - Fully Qualified Domain Names (FQDNs)
  - HTTP/HTTPS URLs
  - Email addresses
  - Cryptographic hashes: MD5 (32 hex), SHA-1 (40 hex), and SHA-256 (64 hex)
- **Safe Processing:** Completely offline—does not perform DNS lookups, HTTP requests, external reputation checks, or execute file attachments.
- **Normalizers & Refang:** Optional refanging support (`--refang`) to safely transform defanged indicators (e.g., `hxxps://`, `[.]`) back into standard forms while retaining the original text.
- **Context Scoring & Warning Lists:** Heuristic context window scoring (`--include-context`) and offline warning-list matching to flag false positives or documentation artifacts.
- **Structured Export:** Generates deterministic JSON (with nested summary counts) and CSV reports.

---

## Realistic Limitations

- **Structural Validation Only:** Validation confirms syntax and structure (e.g., valid IP ranges, proper domain labels, correct hash lengths). It **does not** establish maliciousness or prove active threat behavior.
- **No Reputation or Threat Intelligence Lookups:** The tool relies entirely on local pattern matching, structural checks, and local warning lists. It has no live feeds or threat intelligence API integrations.
- **False Positives / Version Ambiguity:** Software version numbers or timestamps (e.g., `1.2.3.4`) can structurally match an IPv4 address. Heuristic scoring flags ambiguity, but human analyst review remains required.
- **Limited File Formats in v1:** Supports `.txt`, `.log`, `.csv`, `.json`, `.md`, and `.eml`. Binary formats (like `.pdf`, `.docx`, or archives) and email attachments are intentionally ignored for safety.

---

## Installation & Environment Setup

It is recommended to run the tool inside a Python virtual environment.

```powershell
# 1. Create a virtual environment
python -m venv .venv

# 2. Activate the virtual environment
# On Windows (PowerShell):
.\.venv\Scripts\Activate.ps1

# 3. Upgrade pip using the venv's python directly
python -m pip install --upgrade pip

# 4. Install requirements
python -m pip install -r requirements.txt

# 5. Run pytest using the venv's python
pytest -v
```

## Execution Instructions

You can run the tool via the command line using python module execution (`-m src.main`).

### 1. Run against the Clean Report
```powershell
python -m src.main samples/clean_report.txt --include-context --refang --warninglist samples/warninglist_test.json --json output/clean_iocs.json --csv output/clean_iocs.csv
```

### 2. Run against the Messy Log

PowerShell

```powershell
python -m src.main samples/messy_log.log --include-context --json output/log_iocs.json --csv output/log_iocs.csv
```

### 3. Run against the Email Sample (`.eml`)

PowerShell

```powershell
python -m src.main samples/email_sample.eml --include-context --warninglist samples/warninglist_test.json --json output/email_iocs.json --csv output/email_iocs.csv
```

## Possible Future Improvements

- **Directory Batch Processing:** Add a `--input-dir` and glob filtering option to scan entire folders of logs or reports in a single command.

- **IPv6 Support:** Expand IP address validation and extraction logic to support IPv6 notations.

- **Dynamic Warning List Synchronization:** Add optional commands to fetch and cache MISP warning lists locally for offline use.

- **Additional Artifact Formats:** Support parsing structured JSON logs or SIEM export formats natively.
