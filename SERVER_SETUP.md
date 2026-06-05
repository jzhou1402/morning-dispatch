# Morning Dispatch — Server Setup

One change needed on the server: add a secret token to the plants app so
`generate.py` can upload the daily dispatch to `johnzhou.xyz/dispatch`.

---

## 1. Find the plants app directory

```bash
find ~ -name "app.py" | grep plants
```

It should be something like `~/personal-website/plants/app.py`.

---

## 2. Add the secret to the plants app `.env`

```bash
echo 'DISPATCH_SECRET=f97fd4a017f6784f96974a73358264218d265a034e98c549e3b1a5ededa135e5' \
  >> ~/personal-website/plants/.env
```

If there is no `.env` yet, that command creates one.
Verify it was written:

```bash
grep DISPATCH_SECRET ~/personal-website/plants/.env
```

---

## 3. Pull the latest code

```bash
cd ~/personal-website && git pull
```

This brings in the two new `/dispatch` routes added to `plants/app.py`.

---

## 4. Restart the plants app

**If running under systemd:**
```bash
sudo systemctl restart plants   # or whatever the unit is named
sudo systemctl status plants    # confirm it came back up
```

**If running under a process manager (pm2, supervisor):**
```bash
pm2 restart plants
# or
supervisorctl restart plants
```

**If running manually:**
```bash
pkill -f "python.*app.py"
cd ~/personal-website/plants
nohup python app.py &
```

---

## 5. Verify it works

```bash
curl -s https://johnzhou.xyz/dispatch
```

Should return 404 (no dispatch uploaded yet — that's correct).

```bash
curl -s -o /dev/null -w "%{http_code}" \
  -X POST https://johnzhou.xyz/dispatch/upload \
  -H "Authorization: Bearer f97fd4a017f6784f96974a73358264218d265a034e98c549e3b1a5ededa135e5" \
  -H "Content-Type: text/html" \
  --data "<h1>test</h1>"
```

Should return `200`. Then `curl https://johnzhou.xyz/dispatch` should return `<h1>test</h1>`.

---

That's it. The next time `generate.py` runs on your Mac, it will
automatically upload the paper and it will be live at:

**https://johnzhou.xyz/dispatch**
