# Publishing BALE to Zenodo

## Step-by-Step Guide

### Step 1: Create a Zenodo Account
1. Go to [zenodo.org](https://zenodo.org)
2. Click "Sign Up" → Choose "Sign up with GitHub" (recommended)
3. Authorize Zenodo to access your GitHub

### Step 2: Link Your Repository
1. Go to [zenodo.org/account/settings/github](https://zenodo.org/account/settings/github)
2. Find `BALE-project` in your repository list
3. Toggle the switch to **ON** (enable)

### Step 3: Create a GitHub Release
Run these commands in your terminal:

```bash
# Make sure everything is committed
git add .
git commit -m "Prepare v8.0.0 release with research paper"
git push origin main

# Create a tag and release
git tag -a v8.0.0 -m "BALE v8.0.0: Neuro-Symbolic Contract Risk Assessment"
git push origin v8.0.0
```

Then go to GitHub:
1. Go to your repo → "Releases" → "Create a new release"
2. Choose tag: `v8.0.0`
3. Title: `BALE v8.0.0: Neuro-Symbolic Contract Risk Assessment`
4. Description:
```
## 🎉 BALE v8.0.0

A neuro-symbolic framework for bilingual contract risk assessment.

### Key Results
- 📊 97.8% clause type accuracy
- 📊 65.9% risk detection accuracy
- 🌐 Bilingual EN/FR support
- 📚 75,382 training examples

### What's Included
- Fine-tuned Mistral-7B model with LoRA adapters
- Hybrid risk analyzer (100+ patterns)
- Golden test set (91 examples)
- Full research paper

📄 Read the paper: [research/paper.md](research/paper.md)
```
5. Click "Publish release"

### Step 4: Get Your DOI
1. Within minutes, Zenodo will automatically archive your release
2. Go to [zenodo.org/deposit](https://zenodo.org/deposit)
3. Find your BALE deposit
4. Copy your DOI (looks like: `10.5281/zenodo.XXXXXXX`)

### Step 5: Update Your README
Replace the DOI placeholder in README.md:
```markdown
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX)
```

### Step 6: Add Zenodo Metadata (Optional)
Go to your Zenodo deposit and click "Edit" to add:
- **Type**: Software
- **Keywords**: legal-nlp, contract-analysis, risk-assessment, neuro-symbolic-ai
- **License**: MIT
- **Related identifiers**: Link to your paper if published elsewhere

---

## Your DOI Badge

After completing the steps, you'll have:

```markdown
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX)
```

This DOI is:
- **Permanent**: Will always resolve to your work
- **Citable**: Can be used in academic papers
- **Indexed**: Searchable in academic databases

---

## Sharing Your Work

Once published, share:
- **GitHub**: `https://github.com/hamza2masmoudi/BALE-project`
- **DOI**: `https://doi.org/10.5281/zenodo.XXXXXXX`
- **Direct Paper**: `https://github.com/hamza2masmoudi/BALE-project/blob/main/research/paper.md`

Good places to share:
- LinkedIn
- Twitter/X
- r/MachineLearning
- r/LegalTech
- Hacker News
