# AI-Based-Fake-Job-Posting-Detector
A full-stack job verification web application that uses machine learning text classification and database fuzzy matching to analyze listings for potential fraud.


##  Key Features

* **Dual-Verification Pipeline:** Combines real-time NLP text analysis (behavior check) with dynamic fuzzy entity verification (fact check)[cite: 4].
* **Safety Override Logic:** Backend business rules override machine learning classifications and flag listings as suspicious if an AI-approved posting references an unverified company entity.
* **Fuzzy Entity Lookup:** Queries a database of **9,959 company records** using an 85% similarity threshold to fetch ratings, industry tags, headquarters, and employee size metrics.
* **Storage-Efficient Transaction Logging:** Logs historical diagnostic scans, confidence metrics, and 50-character truncated snippets to an SQLite database.
* **Modern High-Contrast UI:** Glassmorphism dashboard featuring real-time loading states, visual status cards, and dynamic UI updates.

## 🛠️ Technical Stack

| Layer | Technologies & Frameworks |
| :--- | :--- |
| **Backend Framework** | Python, FastAPI, Uvicorn |
| **Machine Learning & NLP** | Scikit-Learn (TF-IDF Vectorization), NLTK (WordNet Lemmatizer), Pickle |
| **Data Processing & Matching** | Pandas, TheFuzz (Fuzzy String Matching) |
| **Database & ORM** | SQLite, SQLAlchemy ORM |
| **Frontend UI** | HTML5, CSS3 (Aurora/Mesh Styling), Vanilla JavaScript ES6 (Fetch API) |



## 🚀 Ensure These For Quick Start: 

### 1. Prerequisites
Ensure you have Python 3.9+ installed on your system.

### 2. Clone the Repository
```bash
git clone [https://github.com/your-username/fake-job-detector.git](https://github.com/your-username/fake-job-detector.git)
cd fake-job-detector
```
### 3. Install these  Dependencies

```
pip install fastapi uvicorn pandas thefuzz nltk scikit-learn sqlalchemy
```
### 4. Setup  Your Local Files
* Ensure your serialized model assets (model.pkl and tfidf.pkl) are placed in the project root directory.
* Ensure list_of_companies.csv is positioned in your dataset path.

### 5. Now Launch Application
```
python app.py
```
   
