# Install
```
pip install -r requirement.txt
```

# Edit
Create `.env` file to set the server config.
```
HOST=0.0.0.0
PORT=5000
DEBUG=false
CHROME_VERSION=<input your version of chrome>
```

# Run
```
python main.py
```

# Test
Get list of events in https://lu.ma/sf
```
curl "http://localhost:5000/get_list?url=https://lu.ma/sf"
```

Get detail info in event https://lu.ma/sfsparks1023
```
curl "http://localhost:5000/get_event?url=https://lu.ma/sfsparks1023"
```