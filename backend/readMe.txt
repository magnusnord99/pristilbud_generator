# README - Price Offer Generator

## 1. Install Python

Before running the script, you need to have Python installed on your Mac. You can check if Python is installed by running:

```bash
python3 --version
```

If Python is not installed, install it using Homebrew:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install python3
```

## 2. Install Dependencies

After installing Python, you need to set up the virtual environment and install dependencies.

### 2.1. Activate Virtual Environment (if not activated)
If you are using a virtual environment, navigate to the project directory and activate it:

```bash
cd ~/Desktop/Pristilbud_generator
source venv/bin/activate
```

### 2.2. Install Required Packages
Make sure all required Python packages are installed:

```bash
pip install -r requirements.txt
```

If the `requirements.txt` file does not exist, install dependencies manually:

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client fpdf
```

## 3. Running the Program

Once dependencies are installed, run the main script:

```bash
python write_to_pdf.py
```

## 4. Google API Credentials
Ensure that you have a valid Google API service account credentials file. If missing, follow these steps:

1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Navigate to **IAM & Admin > Service Accounts**.
3. Generate a new **JSON Key** for your service account.
4. Place the file in the correct directory and update `from_google.py` with the correct path:

```python
SERVICE_ACCOUNT_FILE = "~/Desktop/Koding/credentials.json"
```

Alternatively, set it as an environment variable:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="~/Desktop/Koding/credentials.json"
```

## 5. Output
The generated PDF file will be saved in the `Desktop` folder with a dynamic name based on the contact person:

```bash
~/Desktop/Price_offer_<Vår_Kontakt>.pdf
```

## 6. Troubleshooting

- If you encounter `ModuleNotFoundError`, ensure you are running inside the virtual environment.
- If the `credentials.json` file is missing, regenerate it as described in **Section 4**.
- If the PDF is not generated, check for missing or incorrect data in `details.get('Vår kontakt', 'N/A')`.

---

This should be all you need to run the project successfully on a Mac. 😊

