![APC Crawler](https://raw.githubusercontent.com/jtcourtemarche/apc/master/static/img/logo.jpg)

Web interface that converts data sheets from various vendors websites to HTML templates.

Currently written for Python 2.7.15

## Supported vendors:
⋅⋅* APC
⋅⋅* Avocent/Vertiv 

## How to use
```
# Clone repository
git clone https://github.com/jtcourtemarche/apc.git
cd apc

# Install dependencies
pip install -r requirements.txt

# Run
python run.py

# Once running, go to http://localhost:5000 to access web interface
```

## Custom Templates
See example template in `templates/example.html` to get started. 

The crawler defaults to `templates/base.html` as the template. This can be changed in the web interface.
