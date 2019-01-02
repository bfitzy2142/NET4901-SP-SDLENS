from flask import Flask, render_template
import os
import generatetopo
import getip

app = Flask(__name__)
odlControllerList = getip.findController()

@app.route("/")
def index():
    return render_template('home.html')
    
    

@app.route("/topology")
def topology():
    result = generatetopo.run()
    
    if result == 1:
        return render_template('topo-failure.html')
    elif result == 0:
        return render_template('displaytopo.html')
        
@app.route("/controller")
def getControllerIP():
    print(odlControllerList)
    return render_template('settings.html', odlList=odlControllerList)


if __name__ == "__main__":
    app.run(debug=True)

