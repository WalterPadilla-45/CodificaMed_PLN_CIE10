// CodificaMed - Frontend Lógica SPA
const API = {
  config: () => fetch("/api/config").then((r) => r.json()),
  cambiarProveedor: (prov) => fetch("/api/config", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ proveedor: prov }),
  }).then((r) => r.json()),
  codificar: (nota, titulo) => fetch("/api/codificar", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ nota, titulo }),
  }).then((r) => {
    if (!r.ok) return r.json().then((err) => Promise.reject(err.detail || "Error en codificación"));
    return r.json();
  }),
  casosEvaluacion: () => fetch("/api/evaluacion/casos").then((r) => r.json()),
  ejecutarEvaluacion: () => fetch("/api/evaluacion/ejecutar", { method: "POST" }).then((r) => r.json()),
  benchmark: () => fetch("/api/evaluacion/benchmark").then((r) => r.json()),
  catalogo: (q = "") => fetch(`/api/catalogo?q=${encodeURIComponent(q)}`).then((r) => r.json()),
  historial: () => fetch("/api/historial").then((r) => r.json()),
};

let estadoGlobal = {
  proveedorActivo: "ollama",
  config: null,
  ultimoResultado: null,
};

function toast(msg) {
  const el = document.getElementById("toast");
  el.textContent = msg;
  el.classList.add("visible");
  setTimeout(() => el.classList.remove("visible"), 3200);
}

// Router
function enrutar() {
  const hash = window.location.hash.slice(2) || "codificar";
  const vista = hash.split("/")[0];

  document.querySelectorAll(".nav a").forEach((a) => {
    a.classList.toggle("activo", a.dataset.ruta === vista);
  });

  const contenedor = document.getElementById("vista-principal");
  if (vista === "codificar") renderCodificador(contenedor);
  else if (vista === "evaluacion") renderEvaluacion(contenedor);
  else if (vista === "catalogo") renderCatalogo(contenedor);
  else if (vista === "historial") renderHistorial(contenedor);
}

window.addEventListener("hashchange", enrutar);

// Inicializar configuración y modelo
async function initApp() {
  try {
    const cfg = await API.config();
    estadoGlobal.config = cfg;
    estadoGlobal.proveedorActivo = cfg.proveedor_activo;
    actualizarSwitchUI(cfg);
  } catch (err) {
    console.error("Fallo al conectar con el backend", err);
  }
  enrutar();
}

function actualizarSwitchUI(cfg) {
  const btns = document.querySelectorAll(".btn-modelo");
  btns.forEach((btn) => {
    const prov = btn.dataset.proveedor;
    btn.classList.toggle("activo", prov === cfg.proveedor_activo);
    const punto = btn.querySelector(".punto-salud");
    const st = cfg.proveedores?.[prov];
    if (punto) {
      punto.className = "punto-salud " + (st?.disponible ? "punto-ok" : "punto-alerta");
    }
  });
}

document.querySelectorAll(".btn-modelo").forEach((btn) => {
  btn.addEventListener("click", async () => {
    const nuevo = btn.dataset.proveedor;
    try {
      const cfg = await API.cambiarProveedor(nuevo);
      estadoGlobal.config = cfg;
      estadoGlobal.proveedorActivo = cfg.proveedor_activo;
      actualizarSwitchUI(cfg);

      const st = cfg.proveedores?.[nuevo];
      if (nuevo === "claude" && !st?.disponible) {
        toast("Aviso: Claude no tiene ANTHROPIC_API_KEY en .env. Se usará el Motor Clínico RAG+NegEx de respaldo.");
      } else {
        toast(`Proveedor activo: ${nuevo.toUpperCase()} (${cfg.modelo_actual})`);
      }
    } catch (e) {
      toast("Error al cambiar modelo: " + e);
    }
  });
});

// VISTA 1: CODIFICADOR
const CASOS_EJEMPLO = [
  {
    nombre: "Caso 1: DM2 + ITU (Descarta Neumonía)",
    nota: "Paciente masculino de 58 años con antecedentes de HTA y DM2 en tratamiento. Acude por disuria intensa y dolor en hipogastrio de 3 días de evolución, con fiebre de 38.5°C. Niega tos, niega dificultad respiratoria. En examen físico se descarta neumonía. Se diagnostica ITU y se inicia antibioticoterapia.",
  },
  {
    nombre: "Caso 2: Dolor precordial (Descarta IAM)",
    nota: "Femenina de 62 años acude a urgencias por dolor precordial opresivo tras discusión familiar. Presenta cefalea moderada y PA elevada compatible con crisis hipertensiva. Se realiza ECG seriado y enzimas cardíacas: se descarta IAM. Refiere ardor estomacal compatible con gastritis.",
  },
  {
    nombre: "Caso 3: Diarrea + Dolor Abd (Niega Fiebre)",
    nota: "Paciente acude por cuadro de diarrea y dolor abd tipo cólico de 24 horas. Niega fiebre y niega vómitos. Refiere antecedente de lumbalgia crónica por esfuerzo. Se diagnostica EDA de presunto origen infeccioso.",
  },
];

function renderCodificador(contenedor) {
  contenedor.innerHTML = `
    <div class="grid-clinico">
      <!-- Columna Izquierda: Input de Nota Clínica -->
      <div class="card">
        <div class="card-cabecera">
          <h2 class="card-titulo">Nota de Evolución Clínica (Texto Libre)</h2>
          <span style="font-size:0.75rem; color:var(--color-text-muted);">Sin datos de pacientes reales</span>
        </div>

        <div class="barra-ejemplos">
          <span style="font-size:0.78rem; font-weight:600; color:var(--color-text-muted);">Cargar ejemplo:</span>
          ${CASOS_EJEMPLO.map((c, i) => `<button class="btn-ejemplo" data-idx="${i}">${c.nombre}</button>`).join("")}
        </div>

        <form id="form-codificar">
          <div class="form-grupo">
            <textarea id="txt-nota" class="form-textarea" placeholder="Escriba o pegue la nota médica aquí (incluya abreviaturas como HTA, DM2, y negaciones como 'niega fiebre', 'se descarta neumonía')..."></textarea>
          </div>
          <button type="submit" id="btn-procesar" class="btn-primario">
            <span>Codificar con PLN y CIE-10</span>
          </button>
        </form>

        <div id="progreso-pipeline" class="pipeline-fases" style="display:none;"></div>
      </div>

      <!-- Columna Derecha: Resultados y Diagnósticos -->
      <div class="card" id="card-resultados">
        <div class="card-cabecera">
          <h2 class="card-titulo">Diagnósticos y Códigos CIE-10 Sugeridos</h2>
          <span id="badge-duracion" style="font-size:0.75rem; font-weight:600; color:var(--color-primary);"></span>
        </div>

        <div id="contenedor-diagnosticos">
          <p style="color:var(--color-text-dim); font-size:0.88rem; text-align:center; padding:3rem 1rem;">
            Ingrese una nota clínica y presione "Codificar" para ver la asignación CIE-10 con evidencia y análisis de negación.
          </p>
        </div>
      </div>
    </div>
  `;

  // Asignar listeners de ejemplos
  contenedor.querySelectorAll(".btn-ejemplo").forEach((b) => {
    b.addEventListener("click", () => {
      const idx = b.dataset.idx;
      document.getElementById("txt-nota").value = CASOS_EJEMPLO[idx].nota;
    });
  });

  const form = document.getElementById("form-codificar");
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const nota = document.getElementById("txt-nota").value.trim();
    if (!nota) return toast("Por favor ingrese una nota clínica.");

    const btn = document.getElementById("btn-procesar");
    btn.disabled = true;
    btn.innerHTML = "<span>Procesando pipeline CRISP-ML(Q)...</span>";

    const progEl = document.getElementById("progreso-pipeline");
    progEl.style.display = "flex";
    progEl.innerHTML = `<div style="font-size:0.8rem; color:var(--color-text-muted);">Iniciando fases de PLN...</div>`;

    try {
      const resp = await API.codificar(nota);
      estadoGlobal.ultimoResultado = resp;
      pintarPipeline(resp.etapas, progEl);
      pintarDiagnosticos(resp.resultado);
      toast("Codificación CIE-10 completada con éxito.");
    } catch (err) {
      toast("Error: " + err);
      progEl.innerHTML = `<div class="fase-fila estado-error">Error: ${err}</div>`;
    } finally {
      btn.disabled = false;
      btn.innerHTML = "<span>Codificar con PLN y CIE-10</span>";
    }
  });

  // Si ya existía un resultado, volver a pintarlo
  if (estadoGlobal.ultimoResultado) {
    pintarPipeline(estadoGlobal.ultimoResultado.etapas, document.getElementById("progreso-pipeline"));
    pintarDiagnosticos(estadoGlobal.ultimoResultado.resultado);
  }
}

function pintarPipeline(etapas, contenedor) {
  contenedor.style.display = "flex";
  contenedor.innerHTML = etapas.map((e) => `
    <div class="fase-fila">
      <div class="fase-info-izq">
        <span class="badge-fase">${e.fase.split("·")[0].trim()}</span>
        <b>${e.nombre}</b>
      </div>
      <span class="fase-estado estado-${e.estado === "ok" ? "ok" : e.estado === "en_curso" ? "curso" : "pendiente"}">
        ${e.estado === "ok" ? `✓ ${e.duracion_s}s` : e.estado}
      </span>
    </div>
  `).join("");
}

function pintarDiagnosticos(res) {
  const el = document.getElementById("contenedor-diagnosticos");
  const badgeDur = document.getElementById("badge-duracion");
  if (badgeDur) badgeDur.textContent = `Modelo: ${res.modelo} (${res.duracion_s}s)`;

  if (!res.diagnosticos || !res.diagnosticos.length) {
    el.innerHTML = `<p style="padding:1rem; color:var(--color-text-muted);">No se detectaron diagnósticos catalogados.</p>`;
    return;
  }

  el.innerHTML = `
    <div style="background:#f8fafc; border-left:3px solid var(--color-primary); padding:0.6rem 0.8rem; margin-bottom:1rem; font-size:0.83rem;">
      <b>Síntesis clínica:</b> ${res.resumen_caso || "Sin resumen disponible."}
    </div>

    <table class="tabla-clinica">
      <thead>
        <tr>
          <th>Código</th>
          <th>Diagnóstico Oficial</th>
          <th>Estado</th>
          <th>Evidencia Textual (Frase Justificativa)</th>
        </tr>
      </thead>
      <tbody>
        ${res.diagnosticos.map((d) => `
          <tr>
            <td><span class="codigo-tag">${d.codigo_cie10}</span></td>
            <td>
              <b>${d.descripcion_oficial || d.descripcion_cie10}</b><br>
              <small style="color:var(--color-text-muted);">${d.capitulo || ""}</small>
            </td>
            <td>
              <span class="badge-estado ${d.estado === "confirmado" ? "badge-confirmado" : "badge-descartado"}">
                ${d.estado === "confirmado" ? "● Confirmado" : "✕ Descartado / Negado"}
              </span>
            </td>
            <td>
              <div class="evidencia-box">"${d.evidencia_textual}"</div>
              ${d.motivo_descarte ? `<small style="color:#e11d48;">${d.motivo_descarte}</small>` : ""}
            </td>
          </tr>
        `).join("")}
      </tbody>
    </table>
  `;
}

// VISTA 2: EVALUACIÓN Y MÉTRICAS
async function renderEvaluacion(contenedor) {
  contenedor.innerHTML = `<p style="text-align:center; padding:2rem;">Cargando métricas y benchmark de CRISP-ML(Q)...</p>`;

  try {
    const [casos, bench] = await Promise.all([API.casosEvaluacion(), API.benchmark()]);

    contenedor.innerHTML = `
      <div class="card">
        <div class="card-cabecera">
          <div>
            <h2 class="card-titulo">Fase 4 CRISP-ML(Q): Aseguramiento de Calidad y Evaluación Cuantitativa</h2>
            <small style="color:var(--color-text-muted);">Evaluación con métricas (Precisión, Recall, F1) sobre el conjunto patrón de 10 casos clínicos anotados</small>
          </div>
          <button id="btn-evaluar-en-vivo" class="btn-primario">
            <span>Ejecutar Evaluación en Vivo (${estadoGlobal.proveedorActivo.toUpperCase()})</span>
          </button>
        </div>

        <div id="panel-metricas-en-vivo"></div>

        <h3 style="font-size:0.95rem; font-weight:700; margin:1.5rem 0 0.75rem;">Benchmark Comparativo: Modelo Local vs. API Externa</h3>
        <table class="tabla-clinica" style="margin-bottom:1.5rem;">
          <thead>
            <tr>
              <th>Criterio</th>
              <th>${bench.modelo_local.nombre}</th>
              <th>${bench.api_externa.nombre}</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><b>Precisión (P)</b></td>
              <td><b>${(bench.modelo_local.metricas.precision * 100).toFixed(1)}%</b></td>
              <td><b>${(bench.api_externa.metricas.precision * 100).toFixed(1)}%</b></td>
            </tr>
            <tr>
              <td><b>Recall / Sensibilidad (R)</b></td>
              <td><b>${(bench.modelo_local.metricas.recall * 100).toFixed(1)}%</b></td>
              <td><b>${(bench.api_externa.metricas.recall * 100).toFixed(1)}%</b></td>
            </tr>
            <tr>
              <td><b>F1-Score</b></td>
              <td><span class="codigo-tag" style="font-size:1.1rem; color:#059669;">${bench.modelo_local.metricas.f1_score.toFixed(3)}</span></td>
              <td><span class="codigo-tag" style="font-size:1.1rem; color:#2563eb;">${bench.api_externa.metricas.f1_score.toFixed(3)}</span></td>
            </tr>
            <tr>
              <td><b>Tiempo Promedio por Caso</b></td>
              <td>${bench.modelo_local.tiempo_promedio_caso_s} segundos</td>
              <td>${bench.api_externa.tiempo_promedio_caso_s} segundos</td>
            </tr>
            <tr>
              <td><b>Costo Operativo</b></td>
              <td>$0.00 (Gratuito y Offline)</td>
              <td>~$0.004 USD por caso</td>
            </tr>
            <tr>
              <td><b>Soberanía y Privacidad</b></td>
              <td>100% On-Premise (No salen datos médicos)</td>
              <td>Requiere políticas cloud y anonimización</td>
            </tr>
            <tr>
              <td><b>Fortalezas</b></td>
              <td><small>${bench.modelo_local.fortalezas}</small></td>
              <td><small>${bench.api_externa.fortalezas}</small></td>
            </tr>
          </tbody>
        </table>

        <div style="background:#f1f5f9; padding:0.85rem; border-radius:6px; font-size:0.85rem; color:#334155;">
          <b>Conclusión de la Evaluación:</b> ${bench.conclusiones_comparativa}
        </div>
      </div>
    `;

    document.getElementById("btn-evaluar-en-vivo").addEventListener("click", async () => {
      const btn = document.getElementById("btn-evaluar-en-vivo");
      btn.disabled = true;
      btn.textContent = "Ejecutando evaluación...";
      const panel = document.getElementById("panel-metricas-en-vivo");
      panel.innerHTML = `<p style="padding:1rem; font-size:0.85rem; color:var(--color-primary);">Evaluando casos clínicos anotados con ${estadoGlobal.proveedorActivo}...</p>`;

      try {
        const res = await API.ejecutarEvaluacion();
        const g = res.metricas_globales;
        panel.innerHTML = `
          <div class="metricas-grid">
            <div class="metrica-card">
              <div class="metrica-valor">${(g.precision * 100).toFixed(1)}%</div>
              <div class="metrica-etiqueta">Precisión Global</div>
            </div>
            <div class="metrica-card">
              <div class="metrica-valor">${(g.recall * 100).toFixed(1)}%</div>
              <div class="metrica-etiqueta">Recall / Sensibilidad</div>
            </div>
            <div class="metrica-card">
              <div class="metrica-valor" style="color:#059669;">${g.f1_score.toFixed(3)}</div>
              <div class="metrica-etiqueta">F1-Score</div>
            </div>
            <div class="metrica-card">
              <div class="metrica-valor">${g.tp} / ${g.total_esperados}</div>
              <div class="metrica-etiqueta">Aciertos Estrictos (TP)</div>
            </div>
          </div>
        `;
        toast("Evaluación en vivo completada exitosamente.");
      } catch (err) {
        panel.innerHTML = `<p style="color:#dc2626; padding:1rem;">Error en evaluación: ${err}</p>`;
      } finally {
        btn.disabled = false;
        btn.textContent = `Ejecutar Evaluación en Vivo (${estadoGlobal.proveedorActivo.toUpperCase()})`;
      }
    });

  } catch (err) {
    contenedor.innerHTML = `<p style="color:#dc2626; padding:2rem;">Fallo al cargar datos de evaluación: ${err}</p>`;
  }
}

// VISTA 3: CATÁLOGO CIE-10
async function renderCatalogo(contenedor) {
  contenedor.innerHTML = `
    <div class="card">
      <div class="card-cabecera">
        <h2 class="card-titulo">Catálogo Clínico CIE-10 Indexado para RAG</h2>
        <input type="search" id="busq-cat" placeholder="Buscar por código, enfermedad o síntoma..." style="padding:0.4rem 0.8rem; border:1px solid var(--color-border); border-radius:6px; font-size:0.85rem; width:280px;">
      </div>
      <div id="tabla-cat-contenedor"></div>
    </div>
  `;

  async function actualizar(q = "") {
    const items = await API.catalogo(q);
    const tabla = document.getElementById("tabla-cat-contenedor");
    tabla.innerHTML = `
      <table class="tabla-clinica">
        <thead>
          <tr>
            <th>Código</th>
            <th>Descripción Oficial</th>
            <th>Capítulo CIE-10</th>
            <th>Sinónimos y Variantes Clínicas</th>
          </tr>
        </thead>
        <tbody>
          ${items.map((it) => `
            <tr>
              <td><span class="codigo-tag">${it.codigo}</span></td>
              <td><b>${it.descripcion}</b></td>
              <td><small style="color:var(--color-text-muted);">${it.capitulo}</small></td>
              <td>${it.sinonimos.map((s) => `<span class="badge-fase" style="margin-right:3px;">${s}</span>`).join("")}</td>
            </tr>
          `).join("")}
        </tbody>
      </table>
    `;
  }

  actualizar();

  document.getElementById("busq-cat").addEventListener("input", (e) => {
    actualizar(e.target.value);
  });
}

// VISTA 4: HISTORIAL
async function renderHistorial(contenedor) {
  contenedor.innerHTML = `<p style="text-align:center; padding:2rem;">Cargando historial clínico de SQLite...</p>`;
  try {
    const items = await API.historial();
    if (!items.length) {
      contenedor.innerHTML = `
        <div class="card" style="text-align:center; padding:3rem;">
          <h2 class="card-titulo">Historial Vacío</h2>
          <p style="color:var(--color-text-muted); font-size:0.85rem; margin-top:0.5rem;">Aún no se han procesado notas clínicas. Regrese a "Codificador" para comenzar.</p>
        </div>
      `;
      return;
    }

    contenedor.innerHTML = `
      <div class="card">
        <div class="card-cabecera">
          <h2 class="card-titulo">Historial de Codificaciones Clínicas (Persistencia SQLite)</h2>
          <span style="font-size:0.8rem; color:var(--color-text-muted);">${items.length} notas registradas</span>
        </div>
        <table class="tabla-clinica">
          <thead>
            <tr>
              <th>ID</th>
              <th>Título / Resumen</th>
              <th>Modelo</th>
              <th>Confirmados</th>
              <th>Descartados</th>
              <th>Fecha y Hora</th>
              <th>Duración</th>
            </tr>
          </thead>
          <tbody>
            ${items.map((it) => `
              <tr>
                <td><span class="codigo-tag">${it.id}</span></td>
                <td><b>${it.titulo}</b></td>
                <td><small>${it.modelo}</small></td>
                <td><span class="badge-estado badge-confirmado">${it.confirmados}</span></td>
                <td><span class="badge-estado badge-descartado">${it.descartados}</span></td>
                <td><small>${it.creado}</small></td>
                <td>${it.duracion_s}s</td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      </div>
    `;
  } catch (err) {
    contenedor.innerHTML = `<p style="color:#dc2626; padding:2rem;">Error al leer el historial: ${err}</p>`;
  }
}

// Iniciar aplicación
document.addEventListener("DOMContentLoaded", initApp);
