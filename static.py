import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import json

class Anime:
    def __init__(self):
        self.url = "https://ani.gamer.com.tw/animeList.php"
        self.headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"}
        self.session = requests.Session()
        # 所有請求都用同一組 headers
        self.session.headers.update(self.headers)
        response = self.session.get(self.url)
        self.root = BeautifulSoup(response.text, "lxml")
        self.__pages = self.get_pages()
        self.animeList = {}
    
    def get_pages(self):
        t_pageNum = self.root.find(class_="page_number")
        if t_pageNum is not None:
            return int(t_pageNum.find_all("a")[-1].text)
        else:
            return 1

    def __len__(self):
        return self.__pages
    
    def parse_number(self, viewed: str):
        if viewed == "統計中":
            return None
        elif "萬" in viewed:
            try:
                return int(float(viewed.replace("萬", "")) * 10000)
            except ValueError:
                print(f"Error parsing viewed number: {viewed}")
                return None
        else:
            try:
                return int(viewed)
            except ValueError:
                print(f"Error parsing viewed number: {viewed}")
                return None
            
    def parse_episode(self, episode: str):
        try:
            return int(episode[1:-1])
        except Exception as e:
            print(f"Error parsing episode number: {episode} | {e}")
            return None
        
    def parse_time(self, time_str: str):
        try:
            time_str = time_str.replace("年份：", "").strip()
            dt = datetime.strptime(time_str, "%Y/%m")
            return dt.timestamp()
        except Exception as e:
            print(f"Error parsing time: {time} | {e}")
            return None

    def set_anime_from_page(self, page: int, max_retries: int=5):
        for _ in range(max_retries):
            try:
                response = self.session.get(self.url, params={"page": page}, timeout=3)
                self.root = BeautifulSoup(response.text, "lxml")
                theme_list = self.root.find(class_="theme-list-block")
                animes = theme_list.find_all("a", recursive=False)
                break
            except Exception as e:
                self.session.cookies.clear() # 在維修畫面後無效
                print("Waiting for 3 seconds to retry...")
                time.sleep(3)
        else:
            print(f"Warning Page {page} returned unexpected HTML")
            print(self.root.prettify())
            self.animeList = {"message": "被Ban掉了Q_Q"}
            self.save_as_json()
            exit(0)

        for card in animes:
            href = card.get("href")  # e.g. animeRef.php?sn=113750 該動漫的query
            img = card.find("img").get("data-src") # 初始階段 <img> 的 src 是空的或放置佔位圖，等到畫面滾動到圖片附近時才會把 data-src 的值設定回 src 來載入真實圖片
            t_detail = card.find("div", class_="anime-detail-block")
            viewed = self.parse_number(t_detail.find("div", class_="show-view-number").p.text.strip())
            title = t_detail.find("p", class_="theme-name").text.strip()
            timestamp = self.parse_time(t_detail.find("p", class_="theme-time").text.strip())
            episode = self.parse_episode(t_detail.find("span", class_="theme-number").text.strip())
            
            # print(f"{title} | {viewed} | {timestamp} | {episode} | {href} | {img}")
            self.animeList.update({title: {
                "viewed": viewed,
                "time": timestamp,
                "episode": episode,
                "href": href,
                "img": img
            }})

    def run(self):
        for page in range(1, self.__pages+1):
            print(f"Carwling Page {page}/{self.__pages}", end="\r")
            self.set_anime_from_page(str(page))
            time.sleep(0.3) # 休息一秒鐘，避免被導去維修畫面

        print("\n========== All Pages End =========")
        print(f"Total {len(self.animeList)} Animes Found")

    def save_as_json(self):
        with open(f"static.json", 'w', encoding="utf-8") as outFile:
            json.dump(self.animeList, outFile, ensure_ascii=False, indent=2)
            print(f"Saved {len(self.animeList)} Animes to static.json")


if __name__=="__main__":
    anime = Anime()
    anime.run()
    anime.save_as_json()      
    
    