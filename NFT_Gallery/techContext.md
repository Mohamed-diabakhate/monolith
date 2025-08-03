# ⚙️ techContext.md — Solana NFT Downloader

---

## 💡 Goal

Create a script that fetches all NFTs held in a **specific Solana wallet**, using the **Ankr Multichain API**, and downloads associated image files to a macOS-native folder (`~/Pictures/SolanaNFTs/`), **securely fetching the API key from Google Secret Manager**.

---

## 🏗️ Tech Stack

| Layer              | Tech                             | Notes                                           |
| ------------------ | -------------------------------- | ----------------------------------------------- |
| API Provider       | Ankr Multichain RPC              | `ankr_getNFTsByOwner` method                    |
| Secret Management  | Google Secret Manager            | Keeps `ANKR_API_KEY` secure                     |
| Scripting Language | Python 3.8+                      | Simple runtime, works well for local automation |
| HTTP Requests      | `requests`                       | Handles POST to Ankr API                        |
| Cloud Client       | `google-cloud-secret-manager`    | Fetches secret at runtime                       |
| Local FS           | Standard Library `os`, `pathlib` | Manage local folders and filenames              |
| macOS Integration  | Native Photos via `~/Pictures`   | Auto-indexed by macOS Photos app                |
| Container          | Docker                           | To make it portable                             |

---

## 📦 Dependencies (PyPI)

```bash
pip install requests google-cloud-secret-manager
```

---

- No extra dependencies (e.g., IPFS, PIL, etc.)
- No need for Solana client SDK (data comes via Ankr)

---

## **🔐 Secret Flow**

1. Script expects GOOGLE_CLOUD_PROJECT in the environment
2. Uses default ADC (Application Default Credentials)
3. Reads latest version of ANKR_API_KEY
4. Fails early if credentials are missing or inaccessible

---

## **📂 File & Folder Design**

- Output Path: ~/Pictures/SolanaNFTs/
- File Name: Normalized NFT name or tokenId, with extension
- If file already exists, it’s skipped (no re-download)
- Folder is auto-created if missing

---

## **🧪 Assumptions**

- Wallet address is fixed and embedded in script
- User has local Python runtime with required packages
- User’s gcloud environment is authenticated
- macOS Photos indexes from ~/Pictures/ by default
- NFT metadata contains a direct imageUrl (http, not ipfs://)

---

## **⚠️ Known Limitations**

| **Limitation**                    | **Status** |
| --------------------------------- | ---------- |
| No CLI arguments                  | ❌ Not yet |
| No image deduplication by hash    | ❌ Not yet |
| No async/image parallel downloads | ❌ Not yet |
| No IPFS gateway fallback          | ❌ Not yet |
| Works only for Solana NFTs        | ✅ Yes     |
| No pagination in Ankr call        | ✅ Handled |

---

## **🛠️ Extension Ideas**

- Add CLI flags (--wallet, --secret, --output)
- iCloud sync or Apple Photos album scripting
- Cron-based scheduled sync
- Metadata tagging per NFT
