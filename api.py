import requests
import csv
import time

def request_api(url="https://api.jikan.moe/v4/top/anime", total_pages=5):    
    fields = ["mal_id", "title_japanese", "type", "episodes", "score", "scored_by", "rank", "year", "url"]

    count = 0
    with open("api.csv", mode="w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()  

        for page in range(1, total_pages + 1):
            print(f"Carwling Page {page}/{total_pages}", end="\r")
            response = requests.get(url, params={"page": page})
            if response.status_code != 200:
                print(f"Error: {response.status_code}")
                return

            # 轉dict
            # data = json.loads(response.text)
            data = response.json().get("data", [])
            # print(data[1])

            for anime in data:
                count += 1
                writer.writerow({
                    "mal_id": anime.get("mal_id"),
                    "title_japanese": anime.get("title_japanese"),
                    "type": anime.get("type"),
                    "episodes": anime.get("episodes"),
                    "score": anime.get("score"),
                    "scored_by": anime.get("scored_by"),
                    "rank": anime.get("rank"),
                    "year": anime.get("year"),
                    "url": anime.get("url")
                })

            time.sleep(1)  # 避免被API限速

    print(f"Saved {count} Animes to api.csv")

if __name__=="__main__":
    request_api()    