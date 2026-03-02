import asyncio
import os
import csv
from datetime import datetime
from TikTokApi import TikTokApi

# 1. MANUALLY PASTE YOUR MS_TOKEN HERE
MY_ACTUAL_TOKEN = "Q3xdXQiCRQyctDM8ejlWYWNFCktVFLsNmtpIKrrjFx-hiWfwgpvgpG0tITzp9dVanMJrroXhh0VjpiBec9G40Xv7_CsT2JDSno3TVY3Fq1tNVvwFZenxi_ynVakJXefYZ2KrvqZ6eDum61jjcRb10leDrA==" 

TARGET_PROFILE = "daytimelantern1"

async def get_video_data():
    results_list = []
    
    # --- DATE FILTER CONFIGURATION ---
    # Format: YYYY-MM-DD
    start_filter = datetime(2025, 4, 1)   # April 1, 2025
    end_filter = datetime(2026, 1, 20, 23, 59, 59)
    
    async with TikTokApi() as api:
        try:
            await api.create_sessions(
                ms_tokens=[MY_ACTUAL_TOKEN], 
                num_sessions=1, 
                sleep_after=10, 
                headless=False, 
                browser='chromium'
            )
            
            target_username = TARGET_PROFILE
            print(f"--- Fetching videos for @{target_username} between {start_filter.date()} and {end_filter.date()} ---")
            
            user = api.user(username=target_username)
            
            # Increased count to 100 to ensure we find videos in that range
            async for video in user.videos(count=100):
                v_dict = video.as_dict
                ts = v_dict.get('createTime')
                
                if not ts:
                    continue
                
                # Convert TikTok timestamp to datetime object for comparison
                video_datetime = datetime.fromtimestamp(int(ts))

                # 1. If video is NEWER than our end_filter, skip it and keep looking
                if video_datetime > end_filter:
                    continue
                
                # 2. If video is OLDER than our start_filter, stop the loop 
                # (Since TikTok is chronological, everything after this will also be too old)
                if video_datetime < start_filter:
                    print(f"Reached videos older than {start_filter.date()}. Stopping...")
                    break

                # Extraction logic stays the same
                stats = v_dict.get('stats', {})
                author = v_dict.get('author', {})
                author_stats = v_dict.get('authorStats', {})
                has_shop = any(a.get('type') in [5, 6] for a in v_dict.get('anchors', [])) if v_dict.get('anchors') else False
                
                dt_str = video_datetime.strftime('%Y-%m-%d %H:%M:%S')

                row = {
                    "Link": f"https://www.tiktok.com/@{author.get('uniqueId')}/video/{v_dict.get('id')}",
                    "Date": dt_str,
                    "Follower_Count": author_stats.get('followerCount'),
                    "Likes": stats.get('diggCount'),
                    "Comments": stats.get('commentCount'),
                    "Shares": stats.get('shareCount'),
                    "Saves": stats.get('collectCount'),
                    "Has_Shop_Button": "Yes" if has_shop else "No"
                }
                
                results_list.append(row)
                print(f"Processed: {row['Link']} ({dt_str})")

            # --- CSV EXPORT LOGIC ---
            if results_list:
                keys = results_list[0].keys()
                filename = f"{TARGET_PROFILE}_tiktok_filtered_data.csv"
                with open(filename, 'w', newline='', encoding='utf-8') as output_file:
                    dict_writer = csv.DictWriter(output_file, fieldnames=keys)
                    dict_writer.writeheader()
                    dict_writer.writerows(results_list)
                print(f"\n✅ Success! {len(results_list)} videos saved to {filename}")
            else:
                print("\n❌ No videos found within that date range.")

        except Exception as e:
            print(f"Detailed Error: {e}")

if __name__ == "__main__":
    asyncio.run(get_video_data())