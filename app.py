import streamlit as st
import PyPDF2
import googlemaps
from itertools import permutations

st.set_page_config(page_title="Optimalizácia trasy pre rozvoz", layout="centered")
st.title("🚚 Optimalizátor trasy z objednávok")

API_KEY = st.secrets["GOOGLE_MAPS_API"]
START_CITY = "Imel"
gmaps = googlemaps.Client(key=API_KEY)

pdf_file = st.file_uploader("Nahraj PDF s objednávkami", type="pdf")

if pdf_file:
    reader = PyPDF2.PdfReader(pdf_file)
    raw_text = " ".join(page.extract_text() for page in reader.pages if page.extract_text())

    known_cities = ["Nová Baňa", "Lúčnica nad Žitavou", "Rohovce", "Tesárske Mlyňany", "Hliník nad Hronom"]
    found_cities = [city for city in known_cities if city in raw_text]

    if found_cities:
        st.success(f"Nájdené mestá: {', '.join(found_cities)}")
        cities = [START_CITY] + found_cities + [START_CITY]

        def get_total_distance(order):
            total_km = 0
            for i in range(len(order)-1):
                result = gmaps.distance_matrix(order[i], order[i+1], mode="driving")
                km = result["rows"][0]["elements"][0]["distance"]["value"] / 1000
                total_km += km
            return total_km

        min_route = None
        min_distance = float('inf')

        for perm in permutations(found_cities):
            route = [START_CITY] + list(perm) + [START_CITY]
            distance = get_total_distance(route)
            if distance < min_distance:
                min_distance = distance
                min_route = route

        st.subheader("🧭 Optimálna trasa")
        st.markdown(" → ".join(min_route))
        st.info(f"Celková vzdialenosť: {round(min_distance, 1)} km")
    else:
        st.warning("V PDF sa nenašli známe mestá. Skontroluj formát.")
