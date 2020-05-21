# EED


### development run 

```
pip3 install -r requirements.txt
python3 run.py
```

### production run (gunicorn)

```
gunicorn --bind 0.0.0.0:5000 run:app
```