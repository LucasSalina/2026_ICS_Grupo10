/* El formulario funciona con HTML y el servidor; este código agiliza la carga. */
(() => {
  const formulario = document.querySelector("#registration-form");
  const consulta = document.querySelector("#consulta-turnos");
  if (!formulario || !consulta) return;
  document.documentElement.classList.add("js");

  const alerta = document.querySelector("#form-alert");
  if (alerta) {
    alerta.focus({ preventScroll: true });
    requestAnimationFrame(() => alerta.scrollIntoView({ block: "start" }));
  }

  // Elegir actividad o fecha consulta los turnos sin pasar por un botón.
  function consultar(ancla) {
    const destino = consulta.getAttribute("action").split("#")[0];
    consulta.setAttribute("action", `${destino}#${ancla}`);
    document.body.classList.add("is-loading");
    consulta.submit();
  }

  document.querySelectorAll('input[name="actividad"]').forEach((opcion) => {
    opcion.addEventListener("change", () => {
      document.querySelectorAll('input[name="fecha"]').forEach((fecha) => {
        fecha.checked = false;
      });
      consultar("paso-turno");
    });
  });
  document.querySelectorAll('input[name="fecha"]').forEach((fecha) => {
    fecha.addEventListener("change", () => consultar("horario"));
  });

  const cantidad = document.querySelector("#cantidad-personas");
  if (!cantidad) return;
  const tarjetas = [...document.querySelectorAll("[data-participant]")];
  const nota = document.querySelector("#participant-capacity-note");
  const resumenTurno = document.querySelector('[data-summary="turno"]');
  const resumenPersonas = document.querySelector('[data-summary="personas"]');
  const resumenCompacto = document.querySelector('[data-summary="compacto"]');
  const pasos = [...document.querySelectorAll("[data-step]")];
  const boton = formulario.querySelector(".submit-button");
  const sinMovimiento = matchMedia("(prefers-reduced-motion: reduce)");

  const turnoElegido = () => document.querySelector('input[name="horario"]:checked');
  const lugaresDelTurno = () => Number(turnoElegido()?.dataset.cupos || tarjetas.length);
  const personas = (numero) => `${numero} persona${numero === 1 ? "" : "s"}`;

  function mostrarParticipantes({ animar = true } = {}) {
    const lugares = lugaresDelTurno();
    const pedidos = Math.max(0, Math.trunc(Number(cantidad.value)) || 0);
    const visibles = Math.min(pedidos, lugares);
    cantidad.max = String(lugares);

    tarjetas.forEach((tarjeta) => {
      const visible = Number(tarjeta.dataset.participant) <= visibles;
      if (visible && tarjeta.hidden && animar) tarjeta.classList.add("is-entering");
      tarjeta.hidden = !visible;
      tarjeta.querySelectorAll("input, select").forEach((campo) => {
        campo.disabled = !visible;
      });
    });

    if (!turnoElegido()) {
      nota.textContent = "Elegí un turno para ver los lugares disponibles.";
    } else if (pedidos > lugares) {
      nota.textContent = `Este turno tiene ${lugares} lugar${lugares === 1 ? "" : "es"} disponible${lugares === 1 ? "" : "s"}.`;
    } else {
      nota.textContent = `Quedan ${lugares} lugar${lugares === 1 ? "" : "es"} en este turno.`;
    }
    nota.classList.toggle("is-warning", Boolean(turnoElegido()) && pedidos > lugares);
    actualizarResumen(pedidos);
  }

  function actualizarResumen(pedidos) {
    const turno = turnoElegido();
    const hora = turno?.closest("label").querySelector(".choice-title").textContent.trim();
    const fin = hora ? `${String(Number(hora.slice(0, 2)) + 1).padStart(2, "0")}:00` : "";
    if (resumenTurno) resumenTurno.textContent = hora ? `${hora} a ${fin}` : "Sin elegir";
    if (resumenPersonas) resumenPersonas.textContent = personas(pedidos);
    if (resumenCompacto) resumenCompacto.textContent = hora ? `${hora}, ${personas(pedidos)}` : "Elegí fecha y turno";
  }

  // Sendero: el caminante avanza hasta el primer paso pendiente.
  const sendero = document.querySelector(".trail");
  const camino = sendero?.querySelector(".trail-path");
  const caminoHecho = sendero?.querySelector(".trail-done");
  const caminante = sendero?.querySelector(".trail-walker");
  const nodos = sendero ? [...sendero.querySelectorAll(".trail-nodes circle")] : [];
  const largoTotal = camino ? camino.getTotalLength() : 0;
  const largoDeNodo = nodos.map((nodo) => {
    const x = Number(nodo.getAttribute("cx"));
    let mejor = 0;
    let distancia = Infinity;
    for (let largo = 0; largo <= largoTotal; largo += 1) {
      const diferencia = Math.abs(camino.getPointAtLength(largo).x - x);
      if (diferencia < distancia) [mejor, distancia] = [largo, diferencia];
    }
    return mejor;
  });
  let largoActual = 0;
  let recorrido = 0;

  function ubicarCaminante(largo) {
    const punto = camino.getPointAtLength(largo);
    caminante.setAttribute("transform", `translate(${punto.x} ${punto.y})`);
    caminoHecho.style.strokeDashoffset = String(100 - (largo / largoTotal) * 100);
    largoActual = largo;
  }

  function avanzarSendero(completos) {
    if (!sendero) return;
    const destino = largoDeNodo[Math.min(completos, nodos.length - 1)];
    nodos.forEach((nodo, indice) => {
      nodo.classList.toggle("is-done", indice < completos);
      nodo.classList.toggle("is-next", indice === completos);
    });
    sendero.classList.toggle("is-finished", completos >= nodos.length);
    cancelAnimationFrame(recorrido);
    if (sinMovimiento.matches) return ubicarCaminante(destino);
    const origen = largoActual;
    const inicio = performance.now();
    const duracion = 500 + Math.abs(destino - origen) * 4;
    const paso = (ahora) => {
      const t = Math.min((ahora - inicio) / duracion, 1);
      const suave = t < 0.5 ? 2 * t * t : 1 - (-2 * t + 2) ** 2 / 2;
      ubicarCaminante(origen + (destino - origen) * suave);
      if (t < 1) recorrido = requestAnimationFrame(paso);
    };
    recorrido = requestAnimationFrame(paso);
  }

  function marcarPasos() {
    pasos.forEach((paso) => {
      const campos = [...paso.querySelectorAll("input, select")].filter(
        (campo) => !campo.disabled && campo.type !== "button",
      );
      const completo = campos.length > 0 && campos.every((campo) => campo.checkValidity());
      paso.classList.toggle("is-complete", completo);
    });
    const primeroPendiente = pasos.findIndex((paso) => !paso.classList.contains("is-complete"));
    avanzarSendero(primeroPendiente === -1 ? pasos.length : primeroPendiente);
  }

  document.querySelectorAll("[data-step-by]").forEach((control) => {
    control.addEventListener("click", () => {
      const actual = Math.trunc(Number(cantidad.value)) || 0;
      const siguiente = Math.min(Math.max(actual + Number(control.dataset.stepBy), 1), lugaresDelTurno());
      if (siguiente !== actual) {
        cantidad.classList.remove("is-bumping");
        void cantidad.offsetWidth;
        cantidad.classList.add("is-bumping");
      }
      cantidad.value = String(siguiente);
      mostrarParticipantes();
      marcarPasos();
    });
  });

  cantidad.addEventListener("input", () => mostrarParticipantes());
  document.querySelectorAll('input[name="horario"]').forEach((turno) => {
    turno.addEventListener("change", () => mostrarParticipantes());
  });
  formulario.addEventListener("input", marcarPasos);
  formulario.addEventListener("change", marcarPasos);
  tarjetas.forEach((tarjeta) => {
    tarjeta.addEventListener("animationend", () => tarjeta.classList.remove("is-entering"));
  });

  formulario.addEventListener("submit", () => {
    boton.disabled = true;
    boton.setAttribute("aria-busy", "true");
    boton.classList.add("is-sending");
    boton.firstChild.textContent = "Reservando tu lugar… ";
  });
  window.addEventListener("pageshow", () => {
    boton.disabled = false;
    boton.removeAttribute("aria-busy");
    boton.classList.remove("is-sending");
    boton.firstChild.textContent = "Finalizar inscripción ";
    document.body.classList.remove("is-loading");
  });

  mostrarParticipantes({ animar: false });
  marcarPasos();
})();
