#!/usr/bin/env python3
"""
update_comunas.py — Genera comunas-hoy.json para la app "Bencina Hoy".

Lee la pagina oficial de la promo "Copec te Apana" y extrae las comunas del dia.
La pagina publica el listado como TEXTO (verificado), con el formato:
    - Region (codigo): Comuna.
asi que un fetch simple basta. No requiere navegador headless.

Uso:
    python3 update_comunas.py            # genera/actualiza comunas-hoy.json
    python3 update_comunas.py --debug    # solo muestra que detecto, sin escribir
"""
import json, re, sys, datetime, unicodedata, urllib.request

FUENTE = "https://ww2.copec.cl/personas/promociones/copec-te-apana-para-que-te-sigas-moviendo"

COMUNAS = ["Arica","Camarones","Putre","General Lagos","Iquique","Alto Hospicio","Pozo Almonte","Camiña","Colchane","Huara","Pica","Antofagasta","Mejillones","Sierra Gorda","Taltal","Calama","Ollagüe","San Pedro de Atacama","Tocopilla","María Elena","Copiapó","Caldera","Tierra Amarilla","Chañaral","Diego de Almagro","Vallenar","Alto del Carmen","Freirina","Huasco","La Serena","Coquimbo","Andacollo","La Higuera","Paihuano","Vicuña","Illapel","Canela","Los Vilos","Salamanca","Ovalle","Combarbalá","Monte Patria","Punitaqui","Río Hurtado","Valparaíso","Casablanca","Concón","Juan Fernández","Puchuncaví","Quintero","Viña del Mar","Isla de Pascua","Los Andes","Calle Larga","Rinconada","San Esteban","La Ligua","Cabildo","Papudo","Petorca","Zapallar","Quillota","La Calera","Hijuelas","La Cruz","Nogales","San Antonio","Algarrobo","Cartagena","El Quisco","El Tabo","Santo Domingo","San Felipe","Catemu","Llaillay","Panquehue","Putaendo","Santa María","Quilpué","Limache","Olmué","Villa Alemana","Santiago","Cerrillos","Cerro Navia","Conchalí","El Bosque","Estación Central","Huechuraba","Independencia","La Cisterna","La Florida","La Granja","La Pintana","La Reina","Las Condes","Lo Barnechea","Lo Espejo","Lo Prado","Macul","Maipú","Ñuñoa","Pedro Aguirre Cerda","Peñalolén","Providencia","Pudahuel","Quilicura","Quinta Normal","Recoleta","Renca","San Joaquín","San Miguel","San Ramón","Vitacura","Puente Alto","Pirque","San José de Maipo","Colina","Lampa","Tiltil","San Bernardo","Buin","Calera de Tango","Paine","Melipilla","Alhué","Curacaví","María Pinto","San Pedro","Talagante","El Monte","Isla de Maipo","Padre Hurtado","Peñaflor","Rancagua","Codegua","Coinco","Coltauco","Doñihue","Graneros","Las Cabras","Machalí","Malloa","Mostazal","Olivar","Peumo","Pichidegua","Quinta de Tilcoco","Rengo","Requínoa","San Vicente","Pichilemu","La Estrella","Litueche","Marchihue","Navidad","Paredones","San Fernando","Chépica","Chimbarongo","Lolol","Nancagua","Palmilla","Peralillo","Placilla","Pumanque","Santa Cruz","Talca","Constitución","Curepto","Empedrado","Maule","Pelarco","Pencahue","Río Claro","San Clemente","San Rafael","Cauquenes","Chanco","Pelluhue","Curicó","Hualañé","Licantén","Molina","Rauco","Romeral","Sagrada Familia","Teno","Vichuquén","Linares","Colbún","Longaví","Parral","Retiro","San Javier","Villa Alegre","Yerbas Buenas","Chillán","Bulnes","Chillán Viejo","El Carmen","Pemuco","Pinto","Quillón","San Ignacio","Yungay","Quirihue","Cobquecura","Coelemu","Ninhue","Portezuelo","Ránquil","Trehuaco","San Carlos","Coihueco","Ñiquén","San Fabián","San Nicolás","Concepción","Coronel","Chiguayante","Florida","Hualqui","Lota","Penco","San Pedro de la Paz","Santa Juana","Talcahuano","Tomé","Hualpén","Lebu","Arauco","Cañete","Contulmo","Curanilahue","Los Álamos","Tirúa","Los Ángeles","Antuco","Cabrero","Laja","Mulchén","Nacimiento","Negrete","Quilaco","Quilleco","San Rosendo","Santa Bárbara","Tucapel","Yumbel","Alto Biobío","Temuco","Carahue","Cholchol","Cunco","Curarrehue","Freire","Galvarino","Gorbea","Lautaro","Loncoche","Melipeuco","Nueva Imperial","Padre Las Casas","Perquenco","Pitrufquén","Pucón","Saavedra","Teodoro Schmidt","Toltén","Vilcún","Villarrica","Angol","Collipulli","Curacautín","Ercilla","Lonquimay","Los Sauces","Lumaco","Purén","Renaico","Traiguén","Victoria","Valdivia","Corral","Lanco","Los Lagos","Máfil","Mariquina","Paillaco","Panguipulli","La Unión","Futrono","Lago Ranco","Río Bueno","Puerto Montt","Calbuco","Cochamó","Fresia","Frutillar","Los Muermos","Llanquihue","Maullín","Puerto Varas","Castro","Ancud","Chonchi","Curaco de Vélez","Dalcahue","Puqueldón","Queilén","Quellón","Quemchi","Quinchao","Osorno","Puerto Octay","Purranque","Puyehue","Río Negro","San Juan de la Costa","San Pablo","Chaitén","Futaleufú","Hualaihué","Palena","Coyhaique","Lago Verde","Aysén","Cisnes","Guaitecas","Cochrane","O'Higgins","Tortel","Chile Chico","Río Ibáñez","Punta Arenas","Laguna Blanca","Río Verde","San Gregorio","Cabo de Hornos","Antártica","Porvenir","Primavera","Timaukel","Natales","Torres del Paine"]

ALIAS = {"llay llay": "Llaillay"}

def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn").strip()

CANON = {norm(c): c for c in COMUNAS}
CANON_NS = {k.replace(" ", ""): v for k, v in CANON.items()}

def canonizar(nombre):
    n = norm(nombre)
    if n in ALIAS: return ALIAS[n]
    if n in CANON: return CANON[n]
    if n.replace(" ", "") in CANON_NS: return CANON_NS[n.replace(" ", "")]
    return nombre.strip()

def parse_comunas(texto):
    m = re.search(r"comunas de hoy\s*:(.*?)(?:•|Condiciones|El beneficio)", texto, re.S | re.I)
    seg = m.group(1) if m else ""
    items = re.findall(r"\)\s*:\s*([^.\n<]+?)\s*\.", seg)
    items = [i.strip() for i in items if i.strip()]
    if len(items) >= 5:
        return [canonizar(i) for i in items]
    tn = norm(texto)
    return [c for c in COMUNAS if re.search(r"\b" + re.escape(norm(c)) + r"\b", tn)]

def fetch_text(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; BencinaHoyBot/1.0)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        html = r.read().decode("utf-8", "ignore")
    return re.sub(r"<[^>]+>", " ", html)

def main():
    debug = "--debug" in sys.argv
    try:
        texto = fetch_text(FUENTE)
    except Exception as e:
        print(f"ERROR al descargar la pagina: {e}", file=sys.stderr); sys.exit(1)
    comunas = parse_comunas(texto)
    if debug:
        print(f"Comunas detectadas ({len(comunas)}):")
        for c in comunas: print("  ", c)
        if len(comunas) < 5: print("\nADVERTENCIA: muy pocas. Revisa si Copec cambio el formato.")
        return
    if len(comunas) < 5:
        print("Deteccion insuficiente; no se sobrescribe el JSON.", file=sys.stderr); sys.exit(2)
    data = {"fecha": datetime.date.today().isoformat(), "comunas": comunas}
    with open("comunas-hoy.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"OK {data['fecha']}: {len(comunas)} comunas -> comunas-hoy.json")

if __name__ == "__main__":
    main()
