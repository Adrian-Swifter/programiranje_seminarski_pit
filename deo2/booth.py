from tkinter import *

def broj_bitova(x):
    if x >= 0:
        return x.bit_length() + 1
    else:
        return (-x - 1).bit_length() + 1

def binarno(broj, n):
    maska = (1 << n) - 1
    return format(broj & maska, "0" + str(n) + "b")

def booth(C, D):
    n = max(broj_bitova(C), broj_bitova(D))
    if C == -(1 << (n - 1)):
        n = n + 1

    maska = (1 << n) - 1
    bit_znaka = 1 << (n - 1)

    A = 0
    Dreg = D & maska
    p1 = 0
    koraci = []
    koraci.append(("", "početak", A, Dreg, p1))

    for i in range(1, n + 1):
        p0 = Dreg & 1
        par = str(p0) + str(p1)

        if par == "10":
            A = (A - C) & maska
            koraci.append((str(i), "P0P-1=10 -> A=A-C", A, Dreg, p1))
        elif par == "01":
            A = (A + C) & maska
            koraci.append((str(i), "P0P-1=01 -> A=A+C", A, Dreg, p1))

        p1 = Dreg & 1
        Dreg = (Dreg >> 1) | ((A & 1) << (n - 1))
        A = (A >> 1) | (A & bit_znaka)

        if par == "00" or par == "11":
            opis = "P0P-1=" + par + " -> samo pomeranje"
        else:
            opis = "aritm. pomeranje >>1"
        koraci.append((str(i), opis, A, Dreg, p1))

    rezultat = (A << n) | Dreg
    if rezultat & (1 << (2 * n - 1)):
        rezultat = rezultat - (1 << (2 * n))

    return n, koraci, rezultat

def izracunaj():
    canvas.delete("all")
    try:
        C = int(e_c.get())
        D = int(e_d.get())
    except ValueError:
        canvas.create_text(20, 20, anchor=W, fill="red", font=("Courier", 12),
                           text="Greška: C i D moraju biti celi brojevi (npr. 5 i -3).")
        return

    n, koraci, rezultat = booth(C, D)
    font = ("Courier", 12)
    y = 20

    canvas.create_text(20, y, anchor=W, font=font,
                       text="Broj bitova n = %d   (C traži %d, D traži %d)"
                            % (n, broj_bitova(C), broj_bitova(D)))
    y = y + 25
    canvas.create_text(20, y, anchor=W, font=font,
                       text="C = %d = %s    -C = %s" % (C, binarno(C, n), binarno(-C, n)))
    y = y + 25
    canvas.create_text(20, y, anchor=W, font=font,
                       text="D = %d = %s" % (D, binarno(D, n)))
    y = y + 35

    kol = [20, 90, 380, 380 + 12 * n + 40, 380 + 24 * n + 80]
    zaglavlje = ["Korak", "Operacija", "A", "D", "P-1"]
    for j in range(5):
        canvas.create_text(kol[j], y, anchor=W, font=("Courier", 12, "bold"),
                           text=zaglavlje[j])
    y = y + 8
    canvas.create_line(20, y, kol[4] + 60, y)
    y = y + 18

    for (korak, opis, A, Dreg, p1) in koraci:
        if "A-C" in opis:
            boja = "red"
        elif "A+C" in opis:
            boja = "green"
        elif "početak" in opis:
            boja = "black"
        else:
            boja = "blue"
        vrednosti = [korak, opis, binarno(A, n), binarno(Dreg, n), str(p1)]
        for j in range(5):
            canvas.create_text(kol[j], y, anchor=W, font=font, fill=boja,
                               text=vrednosti[j])
        y = y + 22

    y = y + 10
    canvas.create_line(20, y, kol[4] + 60, y)
    y = y + 20
    A_kraj = koraci[-1][2]
    D_kraj = koraci[-1][3]
    canvas.create_text(20, y, anchor=W, font=("Courier", 12, "bold"),
                       text="Rezultat A:D = %s %s = %d"
                            % (binarno(A_kraj, n), binarno(D_kraj, n), rezultat))
    y = y + 25
    if rezultat == C * D:
        provera = "Provera: C * D = %d  ->  TAČNO" % (C * D)
    else:
        provera = "Provera: C * D = %d  ->  GREŠKA" % (C * D)
    canvas.create_text(20, y, anchor=W, font=("Courier", 12, "bold"), text=provera)

    canvas.config(scrollregion=(0, 0, 1200, y + 30))

root = Tk()
root.title("Booth-ov algoritam - množenje označenih brojeva")
root.geometry("950x700")

ulaz = Frame(root)
ulaz.pack(pady=10)

Label(ulaz, text="C (množenik):").grid(row=0, column=0, padx=5)
e_c = Entry(ulaz, width=12)
e_c.grid(row=0, column=1, padx=5)
e_c.insert(0, "2")

Label(ulaz, text="D (množilac):").grid(row=0, column=2, padx=5)
e_d = Entry(ulaz, width=12)
e_d.grid(row=0, column=3, padx=5)
e_d.insert(0, "-3")

Button(ulaz, text="Izračunaj", bg="lightgreen", command=izracunaj).grid(row=0, column=4, padx=10)

okvir = Frame(root)
okvir.pack(fill=BOTH, expand=True, padx=10, pady=10)
scrollbar = Scrollbar(okvir)
scrollbar.pack(side=RIGHT, fill=Y)
canvas = Canvas(okvir, bg="white", yscrollcommand=scrollbar.set)
canvas.pack(side=LEFT, fill=BOTH, expand=True)
scrollbar.config(command=canvas.yview)

izracunaj()
root.mainloop()
