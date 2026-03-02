import instaloader
import csv
from datetime import datetime
from itertools import takewhile, dropwhile

# Initialize Instaloader
L = instaloader.Instaloader()

# --- CONFIGURATION ---
TARGET_PROFILE = "shiftprjct"
START_DATE = datetime(2022, 10, 1)
END_DATE = datetime(2023, 1, 14, 23, 59, 59)

def scrape_with_date_range():
    try:
        profile = instaloader.Profile.from_username(L.context, TARGET_PROFILE)
        posts = profile.get_posts()

        # Filters: newest to oldest logic
        filtered_posts = takewhile(lambda p: p.date_utc >= START_DATE, 
                                   dropwhile(lambda p: p.date_utc > END_DATE, posts))

        all_posts = []
        print(f"Fetching posts from {TARGET_PROFILE}...")

        for post in filtered_posts:
            # SANITY CHECK: If likes are -1, it means Instagram is blocking the data
            current_likes = post.likes
            if current_likes == -1:
                print(f"⚠️ Warning: Likes hidden or blocked for post {post.shortcode}")
            
            print(f"Processing post: {post.shortcode} ({post.date_utc.date()}) | Likes: {current_likes}")
            
            all_posts.append({
                "link": f"https://www.instagram.com/p/{post.shortcode}/",
                "type": post.typename,
                "views": post.video_view_count if post.is_video else 0,
                "likes": current_likes,
                "comments": post.comments,
                "caption": post.caption,
                "date": post.date_utc.isoformat()
            })

        if not all_posts:
            print("No posts found in that date range.")
            return

        filename = f"{TARGET_PROFILE}_data.csv"
        with open(filename, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=["link", "type", "views", "likes", "comments", "caption", "date"])
            writer.writeheader()
            writer.writerows(all_posts)
            
        print(f"✅ Success! Saved {len(all_posts)} posts.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    scrape_with_date_range()