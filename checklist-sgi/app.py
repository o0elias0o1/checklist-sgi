"""Lista de verificación integrada: ISO 9001 · ISO 14001 · ISO 45001."""
import io
from datetime import date

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Checklist SGI ISO 9001/14001/45001", page_icon="✅", layout="wide")

NORMAS = {"9001": "ISO 9001 (Calidad)", "14001": "ISO 14001 (Ambiental)", "45001": "ISO 45001 (SST)"}
OPCIONES = ["Sin evaluar", "Cumple", "Cumple parcialmente", "No cumple", "No aplica"]
PUNTAJE = {"Cumple": 1.0, "Cumple parcialmente": 0.5, "No cumple": 0.0}
ALL = ("9001", "14001", "45001")

CLAUSULAS = {
    4: "Contexto de la organización",
    5: "Liderazgo",
    6: "Planificación",
    7: "Apoyo",
    8: "Operación",
    9: "Evaluación del desempeño",
    10: "Mejora",
}

# (cláusula, tema, pregunta/requisito, normas a las que aplica)
ITEMS_RAW = [
    # 4. Contexto
    (4, "Contexto", "¿Se han identificado las cuestiones internas y externas que afectan el propósito y los resultados del sistema?", ALL),
    (4, "Contexto", "¿Se consideran las condiciones ambientales (clima, calidad del aire/agua, recursos) que pueden afectar a la organización o ser afectadas por ella?", ("14001",)),
    (4, "Partes interesadas", "¿Están identificadas las partes interesadas pertinentes y sus necesidades y expectativas?", ALL),
    (4, "Partes interesadas", "¿Se identifican los requisitos de los trabajadores y de otras partes interesadas en materia de SST?", ("45001",)),
    (4, "Partes interesadas", "¿Se determinaron cuáles necesidades y expectativas se convierten en requisitos legales y otros requisitos?", ("14001", "45001")),
    (4, "Alcance", "¿Está definido y documentado el alcance del sistema (procesos, sedes, actividades, productos y servicios)?", ALL),
    (4, "Sistema de gestión", "¿Están determinados los procesos del sistema, sus entradas, salidas, secuencia e interacción?", ALL),
    # 5. Liderazgo
    (5, "Liderazgo y compromiso", "¿La alta dirección demuestra compromiso: integra el sistema a los procesos del negocio y asegura los recursos?", ALL),
    (5, "Liderazgo y compromiso", "¿La alta dirección promueve el enfoque al cliente y la conformidad de productos y servicios?", ("9001",)),
    (5, "Política", "¿Existe una política (calidad, ambiental, SST o integrada) adecuada al contexto, comunicada y disponible?", ALL),
    (5, "Política", "¿La política incluye compromisos de protección del medio ambiente y prevención de la contaminación?", ("14001",)),
    (5, "Política", "¿La política incluye el compromiso de proporcionar condiciones de trabajo seguras y saludables y eliminar peligros?", ("45001",)),
    (5, "Roles y responsabilidades", "¿Están asignadas, comunicadas y entendidas las responsabilidades y autoridades del sistema?", ALL),
    (5, "Consulta y participación", "¿Existen procesos de consulta y participación de los trabajadores (p. ej. comité paritario, representantes de SST)?", ("45001",)),
    # 6. Planificación
    (6, "Riesgos y oportunidades", "¿Se determinan los riesgos y oportunidades del sistema y se planifican acciones para abordarlos?", ALL),
    (6, "Aspectos ambientales", "¿Se identifican aspectos ambientales (emisiones, residuos, vertimientos, consumo de recursos) y se evalúa su significancia?", ("14001",)),
    (6, "Aspectos ambientales", "¿Se consideran condiciones anormales y de emergencia, y la perspectiva de ciclo de vida, al evaluar aspectos e impactos?", ("14001",)),
    (6, "Peligros SST", "¿Se identifican peligros y se evalúan riesgos de SST de forma continua y proactiva (rutinarias y no rutinarias)?", ("45001",)),
    (6, "Requisitos legales", "¿Se identifica, accede y mantiene actualizada la normativa legal y otros requisitos aplicables?", ("14001", "45001")),
    (6, "Requisitos legales", "¿Se identifican los requisitos legales aplicables a productos y servicios?", ("9001",)),
    (6, "Planificación de acciones", "¿Las acciones planificadas están integradas en los procesos y su eficacia se evalúa?", ALL),
    (6, "Objetivos", "¿Existen objetivos medibles, coherentes con la política, con responsables, plazos y recursos definidos?", ALL),
    (6, "Cambios", "¿Los cambios al sistema se planifican y se evalúa su impacto antes de implementarse?", ALL),
    # 7. Apoyo
    (7, "Recursos", "¿Se determinan y proporcionan los recursos necesarios (personas, infraestructura, ambiente de trabajo)?", ALL),
    (7, "Recursos", "¿Se controlan los recursos de seguimiento y medición (equipos calibrados, trazabilidad metrológica)?", ("9001",)),
    (7, "Competencia", "¿Se determina la competencia necesaria y se asegura mediante formación, experiencia o evaluación?", ALL),
    (7, "Toma de conciencia", "¿El personal conoce la política, sus aportes al sistema y las consecuencias de no cumplir?", ALL),
    (7, "Toma de conciencia", "¿Los trabajadores conocen los peligros, riesgos y su derecho a retirarse de situaciones de peligro grave?", ("45001",)),
    (7, "Comunicación", "¿Existe un proceso de comunicación interna y externa (qué, cuándo, a quién, cómo)?", ALL),
    (7, "Información documentada", "¿La información documentada requerida se crea, actualiza, controla y se encuentra disponible?", ALL),
    # 8. Operación
    (8, "Planificación y control operacional", "¿Se planifican, implementan y controlan los procesos con criterios definidos?", ALL),
    (8, "Control operacional", "¿Se controlan las operaciones asociadas a aspectos ambientales significativos (residuos, efluentes, emisiones, sustancias peligrosas)?", ("14001",)),
    (8, "Ciclo de vida", "¿Se consideran requisitos ambientales en diseño, compras, transporte, uso y disposición final de productos y servicios?", ("14001",)),
    (8, "Jerarquía de controles", "¿Se aplica la jerarquía de controles (eliminar, sustituir, controles de ingeniería, administrativos, EPP)?", ("45001",)),
    (8, "Gestión del cambio", "¿Se gestionan los cambios temporales y permanentes que afecten la SST (nuevos procesos, equipos, personal)?", ("45001",)),
    (8, "Requisitos del producto/servicio", "¿Se determinan, revisan y comunican los requisitos de productos y servicios con los clientes?", ("9001",)),
    (8, "Diseño y desarrollo", "¿Se planifican, controlan y validan las etapas de diseño y desarrollo (si aplica)?", ("9001",)),
    (8, "Proveedores y contratistas", "¿Se evalúan, seleccionan y controlan los proveedores externos y contratistas (calidad, ambiente y SST)?", ALL),
    (8, "Producción y provisión", "¿La producción o prestación del servicio se realiza en condiciones controladas, con identificación y trazabilidad?", ("9001",)),
    (8, "Propiedad del cliente", "¿Se cuida la propiedad del cliente o proveedores externos y se preserva el producto?", ("9001",)),
    (8, "Salidas no conformes", "¿Se identifican y controlan las salidas no conformes para evitar su uso o entrega no intencionada?", ("9001",)),
    (8, "Emergencias", "¿Existen planes de preparación y respuesta ante emergencias (derrames, incendio, sismo, accidentes), con simulacros periódicos?", ("14001", "45001")),
    # 9. Evaluación
    (9, "Seguimiento y medición", "¿Se definen qué, cómo y cuándo se mide, y se analizan y evalúan los resultados (indicadores)?", ALL),
    (9, "Seguimiento ambiental/SST", "¿Se monitorean indicadores ambientales (consumos, emisiones, residuos) y de SST (accidentalidad, ausentismo, salud ocupacional)?", ("14001", "45001")),
    (9, "Satisfacción del cliente", "¿Se hace seguimiento de la percepción y satisfacción del cliente?", ("9001",)),
    (9, "Cumplimiento legal", "¿Se evalúa periódicamente el cumplimiento de requisitos legales y otros requisitos?", ("14001", "45001")),
    (9, "Auditoría interna", "¿Hay un programa de auditorías internas con criterios, auditores imparciales y reporte a la dirección?", ALL),
    (9, "Revisión por la dirección", "¿La alta dirección revisa el sistema a intervalos planificados con entradas y salidas completas?", ALL),
    # 10. Mejora
    (10, "No conformidades", "¿Se reacciona ante no conformidades, se analizan causas raíz y se verifica la eficacia de las acciones correctivas?", ALL),
    (10, "Incidentes", "¿Se investigan incidentes y accidentes de trabajo y se involucra a los trabajadores en el análisis?", ("45001",)),
    (10, "Mejora continua", "¿Se mejora continuamente la idoneidad, adecuación y eficacia del sistema y su desempeño?", ALL),
]

ITEMS = [
    {"id": f"{c}.{i:02d}", "clausula": c, "tema": t, "pregunta": q, "normas": n}
    for i, (c, t, q, n) in enumerate(ITEMS_RAW, start=1)
]


# ---------------------------------------------------------------- utilidades
def respuesta(item_id: str) -> str:
    return st.session_state.get(f"r_{item_id}", "Sin evaluar")


def construir_df(normas_sel):
    filas = []
    for it in ITEMS:
        aplica = [n for n in it["normas"] if n in normas_sel]
        if not aplica:
            continue
        filas.append({
            "ID": it["id"],
            "Cláusula": it["clausula"],
            "Nombre cláusula": CLAUSULAS[it["clausula"]],
            "Tema": it["tema"],
            "Requisito": it["pregunta"],
            "Normas": ", ".join(f"ISO {n}" for n in aplica),
            "_normas": aplica,
            "Respuesta": respuesta(it["id"]),
            "Observaciones": st.session_state.get(f"o_{it['id']}", ""),
        })
    return pd.DataFrame(filas)


def porcentaje(sub: pd.DataFrame):
    ev = sub[sub["Respuesta"].isin(PUNTAJE)]
    if ev.empty:
        return None
    return round(100 * ev["Respuesta"].map(PUNTAJE).mean(), 1)


def nivel(p):
    if p is None:
        return "—"
    if p >= 90:
        return "Alto"
    if p >= 70:
        return "Medio"
    if p >= 50:
        return "Bajo"
    return "Crítico"


# ---------------------------------------------------------------- barra lateral
st.sidebar.title("⚙️ Configuración")
organizacion = st.sidebar.text_input("Organización", placeholder="Nombre de la empresa")
auditor = st.sidebar.text_input("Evaluador", placeholder="Tu nombre")
fecha = st.sidebar.date_input("Fecha", value=date.today())
normas_sel = st.sidebar.multiselect(
    "Normas a evaluar", list(NORMAS), default=list(NORMAS), format_func=lambda n: NORMAS[n]
)
solo_pendientes = st.sidebar.checkbox("Mostrar solo requisitos sin evaluar", value=False)

if st.sidebar.button("🗑️ Reiniciar evaluación"):
    for k in list(st.session_state):
        if k.startswith(("r_", "o_", "plan_")):
            del st.session_state[k]
    st.rerun()

st.sidebar.caption(
    "Preguntas redactadas con base en la estructura de alto nivel (Anexo SL) de las normas. "
    "No reemplazan el texto oficial de las ISO."
)

# ---------------------------------------------------------------- cabecera
st.title("✅ Lista de verificación integrada de Sistemas de Gestión")
st.markdown("**ISO 9001 · ISO 14001 · ISO 45001** — diagnóstico de cumplimiento por cláusulas.")

if not normas_sel:
    st.warning("Selecciona al menos una norma en la barra lateral.")
    st.stop()

df = construir_df(normas_sel)
total, evaluados = len(df), int((df["Respuesta"] != "Sin evaluar").sum())
st.progress(evaluados / total if total else 0, text=f"Avance: {evaluados} de {total} requisitos evaluados")

tab_eval, tab_res, tab_plan, tab_info = st.tabs(["📝 Evaluación", "📊 Resultados", "🛠️ Plan de acción", "ℹ️ Acerca de"])

# ---------------------------------------------------------------- evaluación
with tab_eval:
    for c, nombre in CLAUSULAS.items():
        items_c = [it for it in ITEMS if it["clausula"] == c and any(n in normas_sel for n in it["normas"])]
        if solo_pendientes:
            items_c = [it for it in items_c if respuesta(it["id"]) == "Sin evaluar"]
        if not items_c:
            continue
        hechos = sum(respuesta(it["id"]) != "Sin evaluar" for it in items_c)
        with st.expander(f"Cláusula {c} · {nombre}  ({hechos}/{len(items_c)})", expanded=(c == 4)):
            for it in items_c:
                etiquetas = " ".join(f"`ISO {n}`" for n in it["normas"] if n in normas_sel)
                st.markdown(f"**{it['id']} – {it['tema']}** {etiquetas}")
                st.write(it["pregunta"])
                col1, col2 = st.columns([1, 2])
                col1.selectbox("Respuesta", OPCIONES, key=f"r_{it['id']}", label_visibility="collapsed")
                col2.text_input("Evidencia / observaciones", key=f"o_{it['id']}",
                                placeholder="Evidencia, documento o registro que lo sustenta",
                                label_visibility="collapsed")
                st.divider()

# ---------------------------------------------------------------- resultados
with tab_res:
    df = construir_df(normas_sel)
    global_p = porcentaje(df)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Cumplimiento global", f"{global_p} %" if global_p is not None else "—")
    c2.metric("Nivel", nivel(global_p))
    c3.metric("No conformidades", int((df["Respuesta"] == "No cumple").sum()))
    c4.metric("Cumple parcialmente", int((df["Respuesta"] == "Cumple parcialmente").sum()))

    if evaluados == 0:
        st.info("Aún no hay respuestas. Completa la pestaña **Evaluación**.")
    else:
        st.subheader("Cumplimiento por norma")
        filas_norma = []
        for n in normas_sel:
            sub = df[df["_normas"].apply(lambda x: n in x)]
            filas_norma.append({"Norma": f"ISO {n}", "Cumplimiento (%)": porcentaje(sub) or 0.0,
                                "Nivel": nivel(porcentaje(sub))})
        dfn = pd.DataFrame(filas_norma)
        st.bar_chart(dfn.set_index("Norma")["Cumplimiento (%)"])
        st.dataframe(dfn, hide_index=True, use_container_width=True)

        st.subheader("Cumplimiento por cláusula")
        filas_cl = []
        for c, nombre in CLAUSULAS.items():
            sub = df[df["Cláusula"] == c]
            if sub.empty:
                continue
            filas_cl.append({"Cláusula": f"{c}. {nombre}", "Cumplimiento (%)": porcentaje(sub) or 0.0,
                             "Nivel": nivel(porcentaje(sub))})
        dfc = pd.DataFrame(filas_cl)
        st.bar_chart(dfc.set_index("Cláusula")["Cumplimiento (%)"])
        st.dataframe(dfc, hide_index=True, use_container_width=True)

        st.caption("Escala: Cumple = 100 %, Cumple parcialmente = 50 %, No cumple = 0 %. "
                   "'No aplica' y 'Sin evaluar' no se incluyen en el cálculo. "
                   "Niveles: Alto ≥ 90, Medio ≥ 70, Bajo ≥ 50, Crítico < 50.")

# ---------------------------------------------------------------- plan de acción
with tab_plan:
    brechas = df[df["Respuesta"].isin(["No cumple", "Cumple parcialmente"])].copy()
    if brechas.empty:
        st.info("No hay brechas registradas todavía.")
        plan = pd.DataFrame()
    else:
        st.write("Completa las acciones para cerrar cada brecha detectada.")
        base = brechas[["ID", "Normas", "Tema", "Respuesta"]].copy()
        base["Acción correctiva / de mejora"] = ""
        base["Responsable"] = ""
        base["Fecha límite"] = ""
        plan = st.data_editor(
            base, hide_index=True, use_container_width=True, key="plan_editor",
            disabled=["ID", "Normas", "Tema", "Respuesta"],
        )

# ---------------------------------------------------------------- exportar
def generar_excel() -> bytes:
    resumen = pd.DataFrame({
        "Campo": ["Organización", "Evaluador", "Fecha", "Normas evaluadas", "Cumplimiento global (%)", "Nivel"],
        "Valor": [organizacion, auditor, str(fecha), ", ".join(f"ISO {n}" for n in normas_sel),
                  porcentaje(df) if porcentaje(df) is not None else "—", nivel(porcentaje(df))],
    })
    detalle = df.drop(columns=["_normas"])
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        resumen.to_excel(w, sheet_name="Resumen", index=False)
        detalle.to_excel(w, sheet_name="Checklist", index=False)
        if not plan.empty:
            plan.to_excel(w, sheet_name="Plan de acción", index=False)
        for ws in w.book.worksheets:
            for col in ws.columns:
                ancho = max(len(str(c.value)) if c.value is not None else 0 for c in col)
                ws.column_dimensions[col[0].column_letter].width = min(ancho + 2, 70)
    return buf.getvalue()


st.sidebar.divider()
st.sidebar.subheader("📥 Exportar")
if evaluados:
    st.sidebar.download_button(
        "Descargar Excel", generar_excel(),
        file_name=f"checklist_sgi_{fecha}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    st.sidebar.download_button(
        "Descargar CSV", df.drop(columns=["_normas"]).to_csv(index=False).encode("utf-8-sig"),
        file_name=f"checklist_sgi_{fecha}.csv", mime="text/csv",
    )
else:
    st.sidebar.caption("Evalúa al menos un requisito para habilitar la descarga.")

# ---------------------------------------------------------------- info
with tab_info:
    st.markdown(
        """
**¿Cómo funciona?**
1. Elige las normas a evaluar en la barra lateral.
2. Responde cada requisito en la pestaña *Evaluación* y registra la evidencia.
3. Revisa los porcentajes en *Resultados*.
4. Define acciones para las brechas en *Plan de acción*.
5. Descarga el informe en Excel o CSV.

**Integración:** las tres normas comparten la estructura de alto nivel (cláusulas 4 a 10), por lo
que los requisitos comunes se evalúan una sola vez y se cuentan para cada norma; los requisitos
específicos (aspectos ambientales, peligros de SST, satisfacción del cliente, etc.) solo se
muestran para la norma correspondiente.
        """
    )
