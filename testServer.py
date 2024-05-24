import requests
import threading
import time
import csv
import random

# URL of the website I'm testing, either tested on aviary or on
# my local machine
port = 8080
urls = [f"http://falcon.cs.umanitoba.ca:{port}/image-board/4", f"http://falcon.cs.umanitoba.ca:{port}/image-board/5", f"http://falcon.cs.umanitoba.ca:{port}/text-board/4"]

# urls = [f"http://localhost:{port}/image-board/4",f"http://localhost:{port}/text-board/4",f"http://localhost:{port}/image-board/5",f"http://localhost:{port}/text-board/7", f"http://localhost:{port}/image-board/2"]
urlpaths = [f"http://localhost:{port}/new-board-0", f"http://localhost:{port}/new-board-2", f"http://localhost:{port}/new-board-3"]

# For all of the threads I'll be making
threads = []

timeStart = time.time()

def makeRequest():
    url = random.choice(urls)
    urlpath = random.choice(urlpaths)
    
    # Too inconsistent with POST
    # method = random.choice(['GET', 'POST'])
    method = 'GET'
    if method == 'GET':
        response = requests.get(url)
    else:
        #inconsistent with post so I decided not to include it
        url = urlpath
        data = "Ayo, that is illegal!"
        headers = {"Content-Type": "text/plain"}
        response = requests.post(url, data=data, headers=headers)
    print(f"Response from {url} using {method}: {response.status_code}")

# Make 100 different threads
threads = []
for _ in range(100):
    thread = threading.Thread(target=makeRequest)
    thread.start()
    threads.append(thread)

# Run all threads concurrently
for thread in threads:
    thread.join()

timeEnd = time.time()

# Write to the csv file
# csvFile = open("./single.csv","a",newline='')
csvFile = open("./multi.csv","a",newline='')
csvWriter = csv.writer(csvFile)
csvWriter.writerow((timeEnd-timeStart,))

# Cleanup time
csvFile.close()