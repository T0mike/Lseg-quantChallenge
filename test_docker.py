import urllib.request

# Fetch from the HOST via mapped port 8510
r = urllib.request.urlopen("http://localhost:8510/_stcore/health")
print("Health:", r.status, r.read().decode())

r = urllib.request.urlopen("http://localhost:8510/")
body = r.read().decode()
print("Main page status:", r.status)
print("Content-Type:", r.headers.get("Content-Type"))
print("Body length:", len(body))
print("Has HTML:", "DOCTYPE" in body)
print("Has JS bundle:", "index." in body and ".js" in body)

# Also verify static assets work from host
r = urllib.request.urlopen("http://localhost:8510/_stcore/health")
print("Health re-check:", r.status)
