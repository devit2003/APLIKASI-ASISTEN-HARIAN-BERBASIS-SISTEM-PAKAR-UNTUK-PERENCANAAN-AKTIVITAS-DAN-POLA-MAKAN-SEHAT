from flask import Flask, request, render_template, jsonify
import joblib
import numpy as np
import random

app = Flask(__name__)

# Load model dan encoder
model = joblib.load("model_productivity.pkl")
le_stres = joblib.load("le_stres.pkl")
le_aktivitas = joblib.load("le_aktivitas.pkl")

def buat_jadwal(jam_tidur, jam_kerja, tingkat_stres, aktivitas_lain):
    jadwal = []
    jam = 6

    jadwal.append((f"{jam:02d}.00 - {jam+1:02d}.00", "Bangun & olahraga ringan"))
    jam += 1
    jadwal.append((f"{jam:02d}.00 - {jam+1:02d}.00", "Sarapan & persiapan kerja"))
    jam += 1

    jam_akhir_kerja = jam + jam_kerja
    jadwal.append((f"{jam:02d}.00 - {jam_akhir_kerja:02d}.00", "Fokus kerja/tugas utama"))
    jam = jam_akhir_kerja

    jadwal.append((f"{jam:02d}.00 - {jam+1:02d}.00", "Istirahat & makan siang"))
    jam += 1
    jadwal.append((f"{jam:02d}.00 - {jam+2:02d}.00", "Lanjut kerja ringan"))
    jam += 2
    jadwal.append((f"{jam:02d}.00 - {jam+2:02d}.00", "Aktivitas hobi/refreshing"))
    jam += 2
    jadwal.append((f"{jam:02d}.00 - {jam+3:02d}.00", "Bersosialisasi / keluarga"))
    jam += 3

    aktivitas_relaksasi = "Relaksasi intensif (stres tinggi)" if tingkat_stres == "tinggi" else "Persiapan tidur / relaksasi"
    jadwal.append((f"{jam:02d}.00 - {jam+1:02d}.00", aktivitas_relaksasi))
    jam += 1

    jam_tidur_akhir = (jam + jam_tidur) % 24
    waktu_tidur = f"{jam:02d}.00 - {jam_tidur_akhir:02d}.00" if jam < jam_tidur_akhir else f"{jam:02d}.00 - 06.00"
    jadwal.append((waktu_tidur, "Tidur malam"))

    return jadwal

@app.route("/")
def dashboard():
    return render_template("dashboard.html")

@app.route("/index", methods=["GET", "POST"])
def index():
    prediction = None
    rekomendasi = []
    jadwal_harian = []

    if request.method == "POST":
        jam_tidur = int(request.form["jam_tidur"])
        jam_kerja = int(request.form["jam_kerja"])
        tingkat_stres = request.form["tingkat_stres"]
        aktivitas_lain = request.form["aktivitas_lain"]

        encoded = np.array([
            jam_tidur,
            jam_kerja,
            le_stres.transform([tingkat_stres])[0],
            le_aktivitas.transform([aktivitas_lain])[0]
        ]).reshape(1, -1)

        prediction = model.predict(encoded)[0]

        if jam_tidur < 6:
            rekomendasi.append("Tingkatkan waktu tidur minimal 6 jam per hari.")
        if jam_kerja > 8:
            rekomendasi.append("Kurangi jam kerja jika memungkinkan, istirahat teratur.")
        if tingkat_stres == "tinggi":
            rekomendasi.append("Lakukan aktivitas relaksasi seperti meditasi atau olahraga.")
        if aktivitas_lain in ["scrolling sosial media", "game"]:
            rekomendasi.append("Kurangi aktivitas yang tidak produktif di waktu luang.")

        jadwal_harian = buat_jadwal(jam_tidur, jam_kerja, tingkat_stres, aktivitas_lain)

    return render_template("index.html", prediction=prediction,
                           rekomendasi=rekomendasi, jadwal=jadwal_harian)
@app.route("/food", methods=["GET", "POST"])
def food():
    saran_makanan = []
    if request.method == "POST":
        aktivitas = request.form["aktivitas"]
        waktu = request.form["waktu"]

        if aktivitas == "rendah":
            if waktu == "pagi":
                saran_makanan = ["Oatmeal dengan buah", "Telur rebus", "Teh hangat"]
            elif waktu == "siang":
                saran_makanan = ["Nasi merah + sayur bening", "Tahu tempe", "Air putih"]
            else:
                saran_makanan = ["Sup ayam hangat", "Salad ringan", "Susu rendah lemak"]
        elif aktivitas == "sedang":
            if waktu == "pagi":
                saran_makanan = ["Roti gandum + telur", "Buah segar", "Teh hijau"]
            elif waktu == "siang":
                saran_makanan = ["Nasi + ayam panggang", "Sayur tumis", "Jus segar"]
            else:
                saran_makanan = ["Kentang rebus + telur", "Sayur bening", "Susu"]
        else:  # berat
            if waktu == "pagi":
                saran_makanan = ["Nasi uduk", "Telur + tempe", "Susu protein"]
            elif waktu == "siang":
                saran_makanan = ["Nasi + daging + sayur", "Buah potong", "Air kelapa"]
            else:
                saran_makanan = ["Mie jagung + telur", "Smoothie buah", "Air putih"]

    return render_template("food.html", saran_makanan=saran_makanan)
@app.route('/jadwal')
def jadwal():
    return render_template('jadwal.html')  # file HTML yang tadi kamu minta

@app.route('/submit-jadwal', methods=['POST'])
def submit_jadwal():
    data = request.json  # Ambil data aktivitas dari frontend (jam -> aktivitas)
    
    # Contoh: data = {"06:00 - 07:00": "sarapan", "07:00 - 09:00": "belajar", ...}
    jadwal_final = [(jam, aktivitas) for jam, aktivitas in data.items()]
    
    return jsonify({"status": "success", "jadwal": jadwal_final})
@app.route('/statistik')
def statistik():
    return render_template('statistik.html')
@app.route('/about')
def about():
    return render_template('about.html')


    



if __name__ == "__main__":
    app.run(debug=True)
