⚙️ techContext.md — Solana NFT Downloader

## 🌐 Project

Download all NFTs (images) from a Solana wallet using Ankr's Multichain API. Images are saved to `~/Pictures/SolanaNFTs/` for native display inside the macOS Photos app.

---

## 💼 Use Case

- I want to **see my Solana NFT collection like a photo album** on my Mac.
- I want to **run the script manually** whenever I want to refresh the collection.
- I **don’t want to re-download** NFTs I already saved.
- I want my **Ankr API key stored securely** in Google Secret Manager.

---

## 🔐 Secrets

- `ANKR_API_KEY` is **fetched from Google Secret Manager**
- No secrets are hardcoded
- Secret version: latest (can be parameterized later)

---

## 🖼️ Output Behavior

- NFTs are downloaded **only if they are not already saved**
- Images are stored in:`~/Pictures/SolanaNFTs/`
- File name format:
