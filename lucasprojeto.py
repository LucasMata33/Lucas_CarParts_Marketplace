import streamlit as st
import pandas as pd
import requests
import random
import time

# ---------- Configurações ----------
st.set_page_config(page_title="Lucas CarParts Marketplace", layout="wide")

# ---------- CSS ----------
st.markdown("""
<style>
body { 
    background-color: #f5f7fa; 
    font-family: 'Arial', sans-serif; 
}

.catalogue-container { 
    display: flex; 
    gap: 20px; 
    margin-top: 20px; 
}

.left-panel { 
    flex: 1; 
    display: grid; 
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); 
    gap: 16px; 
}

.card { 
    background-color: #fff; 
    border-radius: 12px; 
    box-shadow: 0 4px 8px rgba(0,0,0,0.1); 
    text-align: center; 
    padding: 10px; 
    transition: transform 0.25s, box-shadow 0.25s, border 0.25s; 
    height: 250px; 
    display: flex; 
    flex-direction: column; 
    justify-content: center; 
    align-items: center; 
    border: 2px solid transparent;
    cursor: pointer;
}

.card:hover { 
    transform: translateY(-5px) scale(1.05); 
    box-shadow: 0 8px 20px rgba(0,0,0,0.2); 
    border: 2px solid #3498db;
}

.card-img { 
    width: 100%; 
    height: 140px; 
    object-fit: contain; 
    border-radius: 8px; 
    margin-bottom: 8px;
}

.card-title { 
    font-size: 13px; 
    font-weight: bold; 
    color: #34495e; 
    text-align: center; 
}

.card-price {
    font-size: 12px;
    color: #27ae60;
    font-weight: bold;
}

.section-title { 
    font-size: 16px; 
    font-weight: bold; 
    margin-bottom: 8px; 
    grid-column: 1 / -1;
}

.loading-dots {
  font-weight: bold;
  font-size: 18px;
  text-align: center;
  color: #2c3e50;
  margin-top: 20px;
  animation: dots 1.5s infinite;
}

@keyframes dots {
  0%   { content: "CARREGANDO"; }
  25%  { content: "CARREGANDO."; }
  50%  { content: "CARREGANDO.."; }
  75%  { content: "CARREGANDO..."; }
}

.stylish-title {
    text-align: center;
    font-size: 60px;
    font-weight: bold;
    background: linear-gradient(90deg, #3498db, #9b59b6, #e74c3c);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: 2px 2px 5px rgba(0,0,0,0.3);
    margin-bottom: 30px;
}
</style>
""", unsafe_allow_html=True)

# ---------- Carregar CSVs ----------
carros_df = pd.read_csv("carros.csv")
pecas_df = pd.read_csv("pecas.csv")

# ---------- Funções ----------
def fetch_images_google(part: str, api_key: str, cse_id: str, num_results=8):
    try:
        response = requests.get(
            "https://www.googleapis.com/customsearch/v1",
            params={"key": api_key, "cx": cse_id, "q": part, "searchType": "image", "num": num_results},
            timeout=10
        ).json()
        return [item["link"] for item in response.get("items", [])]
    except:
        return []

def render_cards(items):
    html = ""
    for idx, item in enumerate(items):
        html += f"""
        <div class="card" onclick="window.open('{item['img']}', '_blank')">
            <img src="{item['img']}" class="card-img"/>
            <div class="card-title">{item['title']}</div>
            <div class="card-price">💲 {item['price']}</div>
        </div>
        """
    st.markdown(html, unsafe_allow_html=True)

# ---------- Sidebar ----------
st.sidebar.header("🔍 Filtros")
marca = st.sidebar.selectbox("Marca", carros_df['Marca'].unique())
modelo = st.sidebar.selectbox("Modelo", carros_df[carros_df['Marca']==marca]['Modelo'].unique())
ano = st.sidebar.selectbox("Ano", carros_df[(carros_df['Marca']==marca) & (carros_df['Modelo']==modelo)]['Ano'].unique())
motor = st.sidebar.selectbox(
    "Motor",
    carros_df[(carros_df['Marca']==marca) & (carros_df['Modelo']==modelo) & (carros_df['Ano']==ano)]['Motor'].unique()
)
peca = st.sidebar.selectbox("Escolha a peça", pecas_df['Peça'].unique())

# ---------- Google API ----------
api_key = "SUA_API_KEY"
cse_id = "SEU_CSE_ID"

# ---------- Histórico ----------
if "history" not in st.session_state:
    st.session_state.history = []

# ---------- Título estilizado ----------
st.markdown('<div class="stylish-title">🔧 Lucas CarParts Marketplace</div>', unsafe_allow_html=True)

# ---------- Main ----------
if st.button("🚗 Buscar peças"):
    st.markdown(f"**Resultados para:** {marca} {modelo} {ano} {motor} - {peca}")

    # Barra de carregamento fake
    loading_text = st.empty()
    for i in range(8):
        loading_text.markdown(f"<div class='loading-dots'>CARREGANDO{'.'*(i%4)}</div>", unsafe_allow_html=True)
        time.sleep(0.4)
    loading_text.empty()

    google_images = fetch_images_google(peca, api_key, cse_id)

    # Gerar preços simulados
    results = []
    for img in google_images:
        preco = f"R$ {random.randint(100, 500)} - R$ {random.randint(600, 1200)}"
        results.append({"title": peca, "img": img, "price": preco})

    st.markdown('<div class="catalogue-container">', unsafe_allow_html=True)
    st.markdown('<div class="left-panel">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🔍 Imagens da peça</div>', unsafe_allow_html=True)

    render_cards(results)

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.session_state.history.append({
        "query": f"{marca} {modelo} {ano} {motor} - {peca}",
        "google_images": google_images
    })

# Histórico visual
if st.session_state.history:
    st.subheader("🔄 Histórico de buscas recentes")
    for h in reversed(st.session_state.history[-5:]):
        st.write(f"- {h['query']}")
