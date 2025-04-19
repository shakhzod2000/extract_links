🔗 Live Link Crawler
A web-based application built with Flask and JavaScript that crawls a given URL, discovers all internal links, and checks their HTTP status codes live using Server-Sent Events (SSE).


🚀 Features
🌐 Crawls a given website and finds all internal hyperlinks

✅ Checks the status code of each link (e.g., 200 OK, 404 Not Found, etc.)

📡 Uses SSE (Server-Sent Events) for real-time link updates

🧠 Smart filtering: ignores irrelevant links like social media, images, JS/CSS files, etc.

📊 Includes a live progress bar and visual feedback for crawling progress

📂 Project Structure
perl
Copy
Edit
📁 extract_links/
├── extract_links.py      # Flask backend (link crawler + SSE stream)
├── templates/
│   └── index.html        # Main frontend interface (JavaScript + HTML + CSS)
└── README.md             # You're here!
🛠️ Technologies Used
Frontend: HTML5, CSS3, Vanilla JavaScript

Backend: Python, Flask

Web Parsing: BeautifulSoup, Requests

Live Updates: Server-Sent Events (SSE)

🧪 How It Works
User submits a website URL.

Flask backend begins crawling and sends back discovered links via SSE.

JavaScript frontend receives links in real-time, checks their status, and displays them with color-coded statuses.

A progress bar tracks the estimated crawl progress.

📦 Installation
🔧 Requirements
Python 3.7+

pip

🧰 Setup
bash
Copy
Edit
git clone https://github.com/shakhzod2000/extract_links.git
cd extract_links

bash
Copy
Edit
pip install flask requests beautifulsoup4
▶️ Run the App
bash
Copy
Edit
python app.py
Then open your browser at:
http://localhost:5000

📸 Screenshots
![image](https://github.com/user-attachments/assets/0be870a6-548a-43d5-add3-7f42d4e4070a)


📋 Example Use Case
Want to check for broken links on your website before deploying? Just paste the URL, hit Start Check, and instantly see which pages need fixing.

🚧 Limitations
Only crawls links within the same domain

Does not parse JavaScript-generated links

Intended for small to medium websites (not optimized for huge sitemaps)

🤝 Contributing
Contributions are welcome! Please open issues or submit PRs.

📬 Contact
For questions or collaboration: 📧 sshermatov@gmail.com
