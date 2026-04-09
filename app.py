from flask import Flask, request, render_template

app = Flask(__name__)

mittaustieto = list() # lista tietojen tallessapitämistä varten

@app.route('/', methods =['GET']) # GET-päätepiste tietojen hakua varten
def index():
    return render_template('index.html', taulukko = mittaustieto)
    #return f"mittaustieto:{mittaustieto[-1]}" # palautetaan merkkijonossa listan viimeinen alkio

@app.route('/lisaa_tieto', methods=['POST']) # POST-päätepiste tietojen vastaanottamista varten
def lisaa_tieto():
    vastaanotettu_data = request.get_json(force=True) #force=True -> tehdään vastaanotetusta JSONista dictionary joka tapauksessa
    mittaustieto.append(vastaanotettu_data["mittaus"]) #lisätään vastaanotettu mittausarvo listaan

    return "ok"

if __name__ == "__main__":
    app.run()