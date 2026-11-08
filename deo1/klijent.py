import socket
import threading
import json
import math
import time
import os
from tkinter import *

HOST = '127.0.0.1'
PORT = 50007

FOLDER = os.path.dirname(os.path.abspath(__file__))

class SinusNit(threading.Thread):
    def __init__(self, canvas, slika_id):
        threading.Thread.__init__(self)
        self.canvas = canvas
        self.slika_id = slika_id
        self.daemon = True

    def run(self):
        x = 15
        dx = 3
        A = 10
        k = 0.03
        while True:
            y = 25 + A * math.sin(k * x)
            self.canvas.coords(self.slika_id, x, y)
            x = x + dx
            if x >= 785 or x <= 15:
                dx = -dx
            time.sleep(0.02)

def posalji(zahtev):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST, PORT))
        s.sendall(json.dumps(zahtev, ensure_ascii=False).encode())

        odgovor = b""
        while True:
            deo = s.recv(1024)
            if not deo:
                break
            odgovor = odgovor + deo
        s.close()

        linije = json.loads(odgovor.decode())
    except ConnectionRefusedError:
        linije = ["Greška: server nije pokrenut (prvo pokreni server.py)."]
    except Exception as e:
        linije = ["Greška: " + str(e)]

    lista.insert(END, ">> " + zahtev["akcija"])
    for linija in linije:
        lista.insert(END, "   " + linija)
    lista.see(END)

def greska(tekst):
    lista.insert(END, "!! " + tekst)
    lista.see(END)

def uzmi_id():
    try:
        return int(e_id.get())
    except ValueError:
        greska("ID mora biti ceo broj.")
        return None

def uzmi_naziv():
    naziv = e_naziv.get().strip()
    if naziv == "":
        greska("Naziv ne sme biti prazan.")
        return None
    return naziv

def kreiraj_tabelu():
    posalji({"akcija": "kreiraj"})

def unos():
    naziv = uzmi_naziv()
    if naziv is None:
        return
    try:
        cena = float(e_cena.get())
    except ValueError:
        greska("Cena mora biti broj (npr. 15000 ili 15000.50).")
        return
    posalji({"akcija": "unos", "naziv": naziv, "cena": cena})

def citaj_po_id():
    id = uzmi_id()
    if id is not None:
        posalji({"akcija": "citaj_id", "id": id})

def citaj_po_nazivu():
    naziv = uzmi_naziv()
    if naziv is not None:
        posalji({"akcija": "citaj_naziv", "naziv": naziv})

def azuriraj_naziv():
    id = uzmi_id()
    if id is None:
        return
    naziv = uzmi_naziv()
    if naziv is not None:
        posalji({"akcija": "azuriraj_naziv", "id": id, "naziv": naziv})

def brisi_po_id():
    id = uzmi_id()
    if id is not None:
        posalji({"akcija": "brisi_id", "id": id})

def brisi_po_nazivu():
    naziv = uzmi_naziv()
    if naziv is not None:
        posalji({"akcija": "brisi_naziv", "naziv": naziv})

def ocisti_listu():
    lista.delete(0, END)

root = Tk()
root.title("KLIJENT - automobili")
root.geometry("800x800")
root.resizable(False, False)

header = Canvas(root, width=800, height=50, bg="lightblue", highlightthickness=0)
header.pack()

slika = PhotoImage(file=os.path.join(FOLDER, "slika.gif"))
slika_id = header.create_image(15, 25, image=slika)

body = Frame(root, width=800, height=700)
body.pack()
body.pack_propagate(False)

forma = Frame(body)
forma.pack(pady=10)

Label(forma, text="ID:").grid(row=0, column=0, sticky=E, padx=5, pady=3)
e_id = Entry(forma, width=30)
e_id.grid(row=0, column=1, pady=3)

Label(forma, text="Naziv:").grid(row=1, column=0, sticky=E, padx=5, pady=3)
e_naziv = Entry(forma, width=30)
e_naziv.grid(row=1, column=1, pady=3)

Label(forma, text="Cena:").grid(row=2, column=0, sticky=E, padx=5, pady=3)
e_cena = Entry(forma, width=30)
e_cena.grid(row=2, column=1, pady=3)

dugmad = Frame(body)
dugmad.pack(pady=5)

Button(dugmad, text="Kreiraj novu tabelu", width=17, bg="orange",
       command=kreiraj_tabelu).grid(row=0, column=0, padx=4, pady=4)
Button(dugmad, text="Unos (naziv, cena)", width=17,
       command=unos).grid(row=0, column=1, padx=4, pady=4)
Button(dugmad, text="Čitaj po ID", width=17,
       command=citaj_po_id).grid(row=0, column=2, padx=4, pady=4)
Button(dugmad, text="Čitaj po nazivu", width=17,
       command=citaj_po_nazivu).grid(row=0, column=3, padx=4, pady=4)
Button(dugmad, text="Ažuriraj naziv (za ID)", width=17,
       command=azuriraj_naziv).grid(row=1, column=0, padx=4, pady=4)
Button(dugmad, text="Obriši po ID", width=17,
       command=brisi_po_id).grid(row=1, column=1, padx=4, pady=4)
Button(dugmad, text="Obriši po nazivu", width=17,
       command=brisi_po_nazivu).grid(row=1, column=2, padx=4, pady=4)
Button(dugmad, text="Očisti listu", width=17,
       command=ocisti_listu).grid(row=1, column=3, padx=4, pady=4)

Label(body, text="Odgovori servera:").pack(anchor=W, padx=10)
okvir_liste = Frame(body)
okvir_liste.pack(fill=BOTH, expand=True, padx=10, pady=(0, 10))

scrollbar = Scrollbar(okvir_liste)
scrollbar.pack(side=RIGHT, fill=Y)
lista = Listbox(okvir_liste, font=("Courier", 10), yscrollcommand=scrollbar.set)
lista.pack(side=LEFT, fill=BOTH, expand=True)
scrollbar.config(command=lista.yview)

footer = Frame(root, width=800, height=50, bg="gray25")
footer.pack()
footer.pack_propagate(False)
Label(footer, text="© 2024 Miloš Drašković RIN-51/25", bg="gray25", fg="white",
      font=("Arial", 12)).pack(expand=True)

nit = SinusNit(header, slika_id)
nit.start()

root.mainloop()
