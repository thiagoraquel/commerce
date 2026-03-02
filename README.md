# CS50W Project 2: Commerce 🛒

An e-commerce auction site where users can create listings, place bids, and manage a personal watchlist. Built with Django and Python as part of Harvard's CS50 Web Programming course.

## 🚀 Features

- **Active Listings:** View all current auction items with real-time price updates (using Django Annotations).
- **Create Listing:** Registered users can post new items for auction.
- **Bidding System:** Validation logic to ensure new bids are higher than current prices.
- **Watchlist:** Personal area to track interesting items using Many-to-Many relationships.
- **Auction Closing:** Owners can end auctions, declaring the highest bidder as the winner.
- **Django Admin:** Full control over the database via the admin interface.

## 🛠️ Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone <your-repo-link>

2. **Activate the Virtual Environment:**
    .\venv\Scripts\activate

3. **Install dependencies**
    pip install -r requirements.txt

4. **Run Migrations:**
    python manage.py makemigrations
    python manage.py migrate

5. **Start the Server:**
    python manage.py runserver ok