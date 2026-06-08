# Panorama 🌌

Panorama is a premium, lightweight, client-side web application designed to help users learn and memorize classic poetry using a **Spaced Repetition System (SRS)**. Inspired by clean iOS design aesthetics, it provides a distraction-free, responsive environment to review and retain poems over time.

---

## 🚀 Features

- **Dashboard**: Track overall progress across categories: **New**, **Learning**, and **Known**.
- **Interactive Flashcards**: Study due poems with a 3D flipping card layout, first-line preview hints, and immediate performance ratings.
- **Spaced Repetition Algorithm**: Adapts next-review times based on how well you remember each poem (`Again`, `Hard`, `Got it`).
- **Comprehensive Library**: A curated collection of classic poems by Wordsworth, Coleridge, Keats, Shakespeare, Blake, Frost, Auden, and more.
- **Local-First & Offline Ready**: All progress is persisted locally in your browser's `LocalStorage`. No servers or databases required.
- **Fast and Lightweight**: Built using vanilla HTML, CSS variables, and modern client-side JavaScript.

---

## 📂 Project Structure

```text
├── index.html       # Application dashboard, progress metrics, and library filter
├── study.html       # Spaced Repetition flashcard learning interface
├── poem.html        # Detailed reader view for individual poems
├── poems.json       # Structured data file containing all poem texts and metadata
├── vercel.json      # Deployment configuration with caching optimizations
├── .gitignore       # Git exclusion list
└── README.md        # Project overview and documentation
```

---

## 🧠 Spaced Repetition Algorithm

Panorama tracks study progress using a custom spaced repetition algorithm configured with the following states:

1. **New**: The poem has not been studied yet.
2. **Learning**: The poem is active in the current session.
3. **Known**: The poem has been successfully recalled and scheduled for future review.

### Review Ratings

- **Again**: Resets interval to 1 day; card remains in the immediate review loop.
- **Hard**: Sets interval to 1 day; card is scheduled for review tomorrow.
- **Got it**: Multiplies the current interval by `2.5` (max 60 days) to space out future reviews.

---

## 🛠️ Getting Started

### Local Development
Since the app fetches the `poems.json` file dynamically, you must serve the files using a local web server to avoid CORS policy blocks.

You can spin up a server instantly with one of the following commands in the project directory:

**Using Python:**
```bash
python3 -m http.server 8000
```

**Using Node.js (`npx`):**
```bash
npx serve .
```

Open `http://localhost:8000` (or the port provided) in your browser.

---

## ☁️ Deployment

The project is pre-configured for deployment on **Vercel** with custom routing and caching:

- Client-side routing is handled gracefully via wildcards.
- Caching rules in `vercel.json` ensure the core static HTML pages load instantly while setting custom TTL headers for `poems.json`.
