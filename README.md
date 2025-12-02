# 🎬 What to Watch? – AI Movie Recommendation System  
A Python + Flask based recommendation engine using IMDb datasets, offering fast search, filtered results, and personalized movie suggestions.

## 📌 Project Overview  
This project is an AI-powered movie recommendation platform that provides:

- 🔍 **Movie Search** (title-based)  
- 🎭 **Genre-based recommendations**  
- 🌍 **Region & language filtering**  
- 🌟 **Personalized recommendations** based on user history  
- ⚡ **Instant loading** using a preprocessed preview dataset  
- 🖥️ **Modern frontend** built with HTML, CSS, JavaScript  
- 🔗 **Backend API** built using Flask

The platform uses IMDb datasets (`basics.tsv`, `ratings.tsv`, `akas.tsv`) to generate a lightweight preview JSON file for fast loading and high performance.

---

## 🚀 Features

### **1. Instant Movie Loading**
IMDb dataset contains over 600,000 movies, but loading this directly takes minutes.  
We use a **preview file (`movies_preview.json`)** built using:

- Movies after **1990**
- Movies with **> 10,000 votes**
- Popular movies sorted by rating

This reduces load time to **less than 1 second**.

### **2. Search Engine**
Search movies by title or genre.  
Top results appear based on IMDb votes and rating.

### **3. Filtered Recommendations**
Filter movies by:
- Genre  
- Region  
- Language  

The backend returns the best-rated movies from the preview dataset.

### **4. Personalized Recommendations**
The system tracks user history in localStorage:
- Genre history  
- Region history  
- Language history  

Then generates dynamic personalized results.

---

## 🏗️ Tech Stack

### **Frontend**
- HTML  
- CSS  
- JavaScript  

### **Backend**
- Python  
- Flask  
- IMDb official datasets  
- JSON preview builder  

### **Tools**
- Git / GitHub  
- VS Code  
- pip / virtual environment  

---

## 📂 Project Structure

```
project/
│
├── app.py
├── movies_preview.json
├── build_preview_modern.py
│
├── imdb/                 # (ignored in GitHub)
│   ├── title.basics.tsv.gz
│   ├── title.ratings.tsv.gz
│   └── title.akas.tsv.gz
│
├── public/
│   ├── index.html
│   ├── script.js
│   └── style.css
│
├── venv/                 # local environment
└── README.md
```

---

## 🔧 Installation & Setup

### **1. Clone the repository**
```
git clone https://github.com/ErrorAayushy/recommen_engin.git
cd recommen_engin
```

### **2. Create virtual environment**
```
python -m venv venv
venv\Scripts\activate
```

### **3. Install dependencies**
```
pip install -r requirements.txt
```

### **4. Run the server**
```
python app.py
```

Your browser will open automatically at:

```
http://localhost:5000
```

---

## 📘 How Preview Dataset Works

Instead of loading 600k+ IMDb movies during runtime, we preprocess them using:

```
python build_preview_modern.py
```

This generates:
```
movies_preview.json
```

This file is loaded instantly on server startup.

---

## 🧪 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/status` | GET | Checks if movie data is loaded |
| `/api/progress` | GET | Loading progress (ETA, %) |
| `/api/search?q=` | GET | Search for movies |
| `/api/recommend/genre` | GET | Recommendations with filters |
| `/api/recommend/personal` | POST | Personalized suggestions |

---

## 🎯 Future Enhancements
- Integrate TMDB API for movie posters  
- Deploy backend online (Render, Railway, Vercel)  
- Add user login + watchlist  
- Add AI embeddings model for similarity (BERT, ANN)  
- Mobile application interface  

---

## 👨‍💻 Team Members

| Name | Role |
|------|------|
| **Aayushy S** | Backend & Integration |
| **Yashvi Shah** | Collaboration Filtering |
| **Princy Thakkar** | Content-Based Filtering |
| **Sonu Thakur** | Backend Engineer |
| **Aanchal Thosar** | Dataset Engineering |

---

## 📜 License
This project is for educational & academic purposes.

---

## ⭐ Acknowledgments
IMDb for providing open datasets.  
Flask and Python community.  
Team members who contributed to development.

