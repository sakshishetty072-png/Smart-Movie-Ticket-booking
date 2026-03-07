import urllib.request
try:
    response = urllib.request.urlopen('http://127.0.0.1:5000/')
    html = response.read().decode()
    print("Server is running!")
    print("First 500 chars:", html[:500])
except Exception as e:
    print(f"Error: {e}")
