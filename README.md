# RoBean ☕ ( in progress )  

A small full-stack project that fetches coffee bean products from multiple online stores,  
lets users filter and sort them, and highlights the cheapest beans per gram.  

## 📷 Snapshots (currently awaiting UI completions)
<img width="2853" height="1470" alt="Screenshot 2025-09-06 141617" src="https://github.com/user-attachments/assets/2b60293f-f8f2-46b9-bc75-d99ee1e40b01" />

# Setup
Have Docker installed and run the following command:
```bash
docker-compose up -d --build
```
Then, access [localhost](http://localhost).

## 🚀 Features
- Scrapes products from multiple coffee store websites (Python + BeautifulSoup)
- FastAPI backend with filtering, sorting, and leaderboard endpoints
- SQLite database + Celery and CRON automated caching
- Simple React frontend for browsing and filtering products
- Unittest for scrapers ( can be ran in docker )

## 🛠 Tech Stack
- Python (FastAPI, BeautifulSoup)
- React+Vite(JavaScript, HTML, CSS, TailwindCSS, shadcn/ui)
- SQLite,Celery,CRON
- Docker

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
<del>- Implement database caching with SQLite or Redis, replacing current caching</del>
- Add user accounts and favorites  
<del>- Schedule automatic refreshes with Celery or CRON, replacing "refresh" logic</del>
- AI chatbot for help
- Newsletter/Notification on product updates
- DB switch SQLite -> Docker and MySQL
