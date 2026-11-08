import socket
import threading
import sqlite3
import json
import os
from tkinter import *

HOST = '127.0.0.1'
PORT = 50007

FOLDER = os.path.dirname(os.path.abspath(__file__))
BAZA = os.path.join(FOLDER, "baza01.db")

def obradi_zahtev(zahtev):
    db = sqlite3.connect(BAZA)
    cursor = db.cursor()
    akcija = zahtev["akcija"]
    odgovor = []

    try:
        if akcija == "kreiraj":
            cursor.execute("DROP TABLE IF EXISTS automobili")
            cursor.execute("""CREATE TABLE automobili (
                                id    INTEGER PRIMARY KEY,
                                naziv TEXT,
                                cena  REAL)""")
            odgovor.append("Kreirana je nova prazna tabela automobili.")

        elif akcija == "unos":
            cursor.execute("INSERT INTO automobili (naziv, cena) VALUES (?, ?)",
                           (zahtev["naziv"], zahtev["cena"]))
            odgovor.append("Unet zapis: id=%d, naziv=%s, cena=%.2f"
                           % (cursor.lastrowid, zahtev["naziv"], zahtev["cena"]))

        elif akcija == "citaj_id":
            cursor.execute("SELECT * FROM automobili WHERE id = ?", (zahtev["id"],))
            odgovor = formatiraj_redove(cursor.fetchall())

        elif akcija == "citaj_naziv":
            cursor.execute("SELECT * FROM automobili WHERE naziv = ?", (zahtev["naziv"],))
            odgovor = formatiraj_redove(cursor.fetchall())

        elif akcija == "azuriraj_naziv":
            cursor.execute("UPDATE automobili SET naziv = ? WHERE id = ?",
                           (zahtev["naziv"], zahtev["id"]))
            odgovor.append("Ažurirano zapisa: %d" % cursor.rowcount)

        elif akcija == "brisi_id":
            cursor.execute("DELETE FROM automobili WHERE id = ?", (zahtev["id"],))
            odgovor.append("Obrisano zapisa: %d" % cursor.rowcount)

        elif akcija == "brisi_naziv":
            cursor.execute("DELETE FROM automobili WHERE naziv = ?", (zahtev["naziv"],))
            odgovor.append("Obrisano zapisa: %d" % cursor.rowcount)

        else:
            odgovor.append("Nepoznata akcija: " + akcija)

        db.commit()
    except Exception as e:
        db.rollback()
        odgovor.append("Greška u bazi: " + str(e))

    db.close()
    return odgovor

def formatiraj_redove(redovi):
    if len(redovi) == 0:
        return ["Nema zapisa koji odgovaraju upitu."]
    linije = []
    for red in redovi:
        linije.append("id=%d, naziv=%s, cena=%.2f" % (red[0], red[1], red[2]))
    return linije

def server_nit():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(5)
    upisi("Server sluša na %s:%d" % (HOST, PORT))

    while True:
        conn, addr = s.accept()
        try:
            podaci = conn.recv(4096).decode()
            upisi("ZAHTEV  " + str(addr) + ": " + podaci)

            zahtev = json.loads(podaci)
            odgovor = obradi_zahtev(zahtev)

            for linija in odgovor:
                upisi("ODGOVOR: " + linija)
            conn.sendall(json.dumps(odgovor, ensure_ascii=False).encode())
        except Exception as e:
            upisi("GREŠKA: " + str(e))
        conn.close()

def upisi(tekst):
    lista.insert(END, tekst)
    lista.see(END)

root = Tk()
root.title("SERVER - baza01.db")
root.geometry("1000x800")

Label(root, text="Zahtevi klijenta i odgovori servera",
      font=("Arial", 14, "bold")).pack(pady=5)

okvir = Frame(root)
okvir.pack(fill=BOTH, expand=True, padx=10, pady=10)

scrollbar = Scrollbar(okvir)
scrollbar.pack(side=RIGHT, fill=Y)

lista = Listbox(okvir, font=("Courier", 10), yscrollcommand=scrollbar.set)
lista.pack(side=LEFT, fill=BOTH, expand=True)
scrollbar.config(command=lista.yview)

t = threading.Thread(target=server_nit, daemon=True)
t.start()

root.mainloop()
