# RoBean ☕ ( in progress )  

A small full-stack project that fetches coffee bean products from multiple online stores,  
lets users filter and sort them, and highlights the cheapest beans per gram.  

## 🚀 Features
- Scrapes products from multiple coffee store websites (Python + BeautifulSoup)
- FastAPI backend with filtering, sorting, and leaderboard endpoints
- Basic caching to improve speed
- Simple React frontend for browsing and filtering products

## 🛠 Tech Stack
- Python (FastAPI, BeautifulSoup)
- React+Vite(JavaScript, HTML, CSS, TailwindCSS, shadcn/ui)
- In-memory caching (no database yet)

## 🎯 Learning Goals
My first solo full-stack project, focused on:
- Web scraping
- API development
- React frontend basics
- UI design
- Data normalization
- Basic caching for performance

## 💡 Future Improvements
- Add more coffee store scrapers  
- Implement database caching with SQLite or Redis, replacing current caching  
- Add user accounts and favorites  
- Schedule automatic refreshes with Celery or CRON, replacing "refresh" logic
- AI chatbot for help
- Newsletter/Notification on product updates
