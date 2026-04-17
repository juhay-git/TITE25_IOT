from flask import Flask, request, render_template, Response, stream_with_context
import json
import threading

app = Flask(__name__)

mittaustieto = dict() # tähän vaihdettiin dictionary
uusi_mittaus = None
condition = threading.Condition()

@app.route('/', methods =['GET']) # GET-päätepiste tietojen hakua varten
def index():
    return render_template('index.html', taulukko = mittaustieto)
    #return f"mittaustieto:{mittaustieto[-1]}" # palautetaan merkkijonossa listan viimeinen alkio

@app.route('/lisaa_tieto', methods=['POST']) # POST-päätepiste tietojen vastaanottamista varten
def lisaa_tieto():
    global uusi_mittaus
    vastaanotettu_data = request.get_json(force=True) #force=True -> tehdään vastaanotetusta JSONista dictionary joka tapauksessa
    mittaus = vastaanotettu_data["mittaus"]

    with condition:
        #mittaustieto.append(mittaus) #lisätään vastaanotettu mittausarvo listaan
        mittaustieto.update(mittaus) # nyt päivitetään dictionaryyn uusi avain/arvo pari
        uusi_mittaus = mittaus
        condition.notify_all()

    return "ok"

@app.route("/stream")
def stream():
    def event_stream():
        while True:
            with condition:
                condition.wait()
                data = uusi_mittaus

            viesti = {
                "mittaus":data
            }
            yield f"data: {json.dumps(viesti)}\n\n"
    
    return Response(
        stream_with_context(event_stream()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control":"no-cache",
            "Connection":"keep-alive"
        }
    )


if __name__ == "__main__":
    app.run()