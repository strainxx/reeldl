import time
import bs4
import requests


def reduce(array: list, reducer, initial=None):
    res = array[0]
    # print("Reduce:",array, reducer, initial)
    st = 1
    if initial is not None:
        res = initial
        st = 0 #array.index(initial)
    for i in range(st, len(array)):
        # print("Before:", res)
        x = reducer(res, array[i], i)
        # print("Return:", x)
        res = x if x is not None else res
        # print("After:", res)
    # print(res)
    return res


def decodeChar(d, e, f):
    # print("Input:",d,e,f)
    charMap = list("0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ+/")
    h = charMap[0:e]
    i = charMap[0:f]
    temp = list(d)
    temp.reverse()
    temp = list(map(int, temp))
    def reducer_d(accumulator, current, index):
        h_id = -1
        current = str(current)
        if current in h:
            h_id = h.index(current)
        else:
            print("Not in h", current, h)
        if h_id!=-1:
            res = accumulator + h.index(current) * pow(e, index)
            accumulator += h.index(current) * pow(e, index)
            return res
        else:
            return accumulator
    j = reduce(temp, reducer_d, 0)
    # print(j)

    k = ""
    while j>0:
        k = i[j%f] + k
        j = (j-j%f)//f
        # print(k, j)

    # print(k if k!="" else "0")
        
    return k if k!="" else "0"

def deobfuscate(string, unused, key, charOffset, e, result):
    result = ""
    len_ = len(string)
    i = 0
    while i < len_:
        s = ""
        while (string[i] != key[e]):
            s += string[i]
            i += 1
        j = 0
        while j < len(key):
            s = s.replace(key[j], str(j))
            j+=1
        result += chr(int(decodeChar(s, e, 10)) - charOffset)
        # print(result)
        i+=1
    # print(result)
    return result

def instagram_download_video(url: str, save_path: str):
    print(f"[DOWNLOADER] Instagram: Downloading video {url}...")
    if not "reel" in url:
        raise Exception("Only reels are supported")
    
    t = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:132.0) Gecko/20100101 Firefox/132.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        # 'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Referer': 'https://www.google.com/',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-User': '?1',
        'Priority': 'u=0, i',
        # Requests doesn't support trailers
        # 'TE': 'trailers',
    }

    
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:132.0) Gecko/20100101 Firefox/132.0',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        # 'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://snapinsta.app',
        'Connection': 'keep-alive',
        'Referer': 'https://snapinsta.app/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Priority': 'u=0',
        # Requests doesn't support trailers
        # 'TE': 'trailers',
    }
    with requests.Session() as s:
        response = s.get('https://snapinsta.app/', headers=t)
        soup = bs4.BeautifulSoup(response.text, "lxml")

        token = soup.find("input", attrs={"name": "token"}).get("value")
        # print("TOKEN:", token)

        resp = requests.post('https://snapinsta.app/action2.php', headers=headers, data={
            'token': token,
            'action': 'post',
            'url': url
        })
        # print(resp.text)

        params = resp.text.split("decodeURIComponent(escape(r))}(")[1].split(")")[0].split(",")
        obf = params[0].strip("\"")
        df = deobfuscate(obf, 0, params[2].strip("\""), int(params[3]), int(params[4]), int(params[5]))
        # print(df)
        print("extracting...")
        soup = bs4.BeautifulSoup(df, "lxml")
        links = soup.find_all("a")
        l = []
        for link in links:
            # print(link.get("href"))
            l.append(link.get("href"))
        v = s.get(l[-3].strip("\"'\\")).content
        with open(save_path, "wb") as f:
            f.write(v)
        return save_path
    
if __name__ == "__main__":
    import sys
    # instagram_download_video("https://www.instagram.com/reel/DC3Inq9soBg/?utm_source=ig_web_copy_link",str(time.time())+".mp4")
    link = sys.argv[1]
    fname = "reeldl.mp4"
    if len(sys.argv) > 2:
        fname = sys.argv[2]
    instagram_download_video(link, fname)
