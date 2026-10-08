import instaloader
import csv
from datetime import datetime
from itertools import takewhile, dropwhile


L = instaloader.Instaloader()


TARGET_PROFILE = "ussfeeds"
START_DATE = datetime(2026, 9, 1)
END_DATE = datetime(2026, 10, 6)

def scrape_with_date_range():
    try:
        profile = instaloader.Profile.from_username(L.context, TARGET_PROFILE)
        posts = profile.get_posts()

        all_posts = []
        print(f"Fetching posts from {TARGET_PROFILE}...")

        for post in posts:
            post_date = post.date_utc
            
            # 1. Skip posts that are newer than our target end date
            if post_date > END_DATE:
                continue
                
            # 2. Stop scrolling if we hit a post older than our start date
            if post_date < START_DATE:
                # IMPORTANT: Check if it's a pinned post. Pinned posts break the timeline.
                # If it's pinned, just skip it and keep scrolling. If not, stop the script.
                if getattr(post, 'is_pinned', False):
                    continue
                else:
                    print(f"Reached posts older than {START_DATE.date()}. Stopping scroll.")
                    break

            # 3. If the script gets here, the post is perfectly within our date range!
            current_likes = post.likes
            if current_likes == -1:
                print(f"⚠️ Warning: Likes hidden or blocked for post {post.shortcode}")
            
            print(f"Processing post: {post.shortcode} ({post_date.date()}) | Likes: {current_likes}")
            
            all_posts.append({
                "link": f"https://www.instagram.com/p/{post.shortcode}/",
                "type": post.typename,
                "views": post.video_view_count if post.is_video else 0,
                "likes": current_likes,
                "comments": post.comments,
                "caption": post.caption,
                "date": post_date.isoformat()
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