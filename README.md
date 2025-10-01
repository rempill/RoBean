# RoBean ☕ ( in progress )  

A small full-stack project that fetches coffee bean products from multiple online stores,  
lets users filter and sort them, and highlights the cheapest beans per gram.  

## 📷 Snapshots (currently awaiting UI completions)
Desktop
<img width="600" alt="screenshot-1759325807377" src="https://github.com/user-attachments/assets/10974fc8-a71e-46da-9b7f-e7b5244dd993" />

Mobile (Samsung Galaxy S20 Ultra)
<img width="200" alt="screenshot-1759325868903" src="https://github.com/user-attachments/assets/d147e5b7-f7aa-45ea-b465-2c1f93bb46a4" />

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
