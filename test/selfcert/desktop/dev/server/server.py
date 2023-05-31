from flask import Flask, render_template
app = Flask(__name__)

# Routes
@app.route('/')
def index():
    return render_template('/Users/tylerretzlaff/Desktop/Projects/Raptor/Raptor/raptor-cli/test/selfcert/desktop/dev/index.html')

if __name__ == '__main__':
    app.run()
    