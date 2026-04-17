from flask import Flask, request, render_template, Response, stream_with_context
import json
import sqlite3
import threading

app = Flask(__name__)


#mittaustieto = dict() # tähän vaihdettiin dictionary
uusi_mittaus = None
condition = threading.Condition()

#tietokannan teko käynnistyksessä, jos ei jo olemassa
yhteys = sqlite3.connect("mittaukset.db3")
kursori = yhteys.cursor()
kursori.execute("""
    CREATE TABLE IF NOT EXISTS mittaukset (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        aika TEXT,
        lampotila INTEGER
    )
""")
yhteys.commit()
yhteys.close()

@app.route('/', methods =['GET']) # GET-päätepiste tietojen hakua varten
def index():
    yhteys = sqlite3.connect("mittaukset.db3")
    kursori = yhteys.cursor()
    kursori.execute("SELECT aika, lampotila FROM mittaukset ORDER BY id ASC")
    tiedot = kursori.fetchall()
    yhteys.close()

    return render_template('index.html', taulukko = tiedot)
    #return render_template('index.html', taulukko = mittaustieto)
    #return f"mittaustieto:{mittaustieto[-1]}" # palautetaan merkkijonossa listan viimeinen alkio

@app.route('/lisaa_tieto', methods=['POST']) # POST-päätepiste tietojen vastaanottamista varten
def lisaa_tieto():
    global uusi_mittaus
    vastaanotettu_data = request.get_json(force=True) #force=True -> tehdään vastaanotetusta JSONista dictionary joka tapauksessa
    mittaus = vastaanotettu_data["mittaus"]

     # {"mittaus": {"2026-04-17T10:10:32": 23}}
    aika, lampotila = next(iter(mittaus.items()))

    yhteys = sqlite3.connect("mittaukset.db3")
    kursori = yhteys.cursor()
    kursori.execute(
        "INSERT INTO mittaukset (aika, lampotila) VALUES (?, ?)",
        (aika, lampotila)
    )
    yhteys.commit()
    yhteys.close()

    with condition:
        #mittaustieto.append(mittaus) #lisätään vastaanotettu mittausarvo listaan
        #mittaustieto.update(mittaus) # nyt päivitetään dictionaryyn uusi avain/arvo pari
        #uusi_mittaus = mittaus
        uusi_mittaus = {aika: lampotila}
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