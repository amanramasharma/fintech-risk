const el = id => document.getElementById(id)

const api = {
  health: "/health",
  ready: "/ready",
  score: "/risk/score",
  scoreExplain: "/risk/score?explain=1"
}

const state = {
  runs: []
}

const toast = (msg) => {
  const t = el("toast")
  t.textContent = msg
  t.style.display = "block"
  clearTimeout(toast._t)
  toast._t = setTimeout(() => t.style.display = "none", 1600)
}

const setStatus = (msg) => el("status").textContent = msg || ""

const num = (v) => {
  if (v === "" || v === null || v === undefined) return undefined
  const n = Number(v)
  return Number.isFinite(n) ? n : undefined
}

const buildPayload = () => {
  const fraud = {
    txn_amount: num(el("txn_amount").value),
    txn_currency: (el("txn_currency").value || "").trim() || undefined,
    txn_country: (el("txn_country").value || "").trim() || undefined,
    avg_txn_amount_30d: num(el("avg_txn_amount_30d").value),
    txns_1h: num(el("txns_1h").value),
    txns_24h: num(el("txns_24h").value),
    account_age_days: num(el("account_age_days").value),
    device_change_7d: num(el("device_change_7d").value),
    failed_logins_24h: num(el("failed_logins_24h").value)
  }

  Object.keys(fraud).forEach(k => fraud[k] === undefined && delete fraud[k])

  const textVal = (el("text").value || "").trim()
  const hasText = textVal.length > 0

  const payload = {}
  if (Object.keys(fraud).length) payload.fraud = fraud

  if (hasText) {
    payload.text = {
      case_id: (el("case_id").value || "").trim() || "C-1001",
      channel: (el("channel").value || "").trim() || "chat",
      customer_id: (el("customer_id").value || "").trim() || "U-1",
      text: textVal
    }
  }

  return payload
}

const bandClass = (band) => {
  const b = (band || "").toLowerCase()
  if (b.includes("low")) return "low"
  if (b.includes("med")) return "medium"
  if (b.includes("high")) return "high"
  return ""
}

const fmt = (x) => {
  if (x === null || x === undefined) return "—"
  if (typeof x === "number") return Number(x).toFixed(2).replace(/\.00$/, ".00")
  return String(x)
}

const groupEvidence = (arr) => {
  const m = new Map()
  for (const e of (arr || [])) {
    const k = (e.source || "unknown").split(".")[0]
    if (!m.has(k)) m.set(k, [])
    m.get(k).push(e)
  }
  return Array.from(m.entries())
}

const render = (resp) => {
  el("rawJson").textContent = JSON.stringify(resp, null, 2)

  const d = resp && resp.decision ? resp.decision : null
  if (!d) return

  el("metaLine").textContent = `audit_id=${resp.audit_id || "—"}  request_id=${resp.request_id || "—"}`

  el("finalCategory").textContent = d.risk_category || "—"
  el("riskScore").textContent = fmt(d.risk_score)

  const band = d.metadata && d.metadata.risk_band ? d.metadata.risk_band : "—"
  el("riskBand").className = `badge ${bandClass(band)}`
  el("riskBand").textContent = band

  const sev = d.metadata && (d.metadata.severity ?? d.metadata.base_score)
  el("severityLine").textContent = sev !== undefined ? `severity: ${fmt(sev)}` : ""

  const reasons = el("reasons")
  reasons.innerHTML = ""
  ;(d.reasons || []).forEach(r => {
    const li = document.createElement("li")
    li.textContent = r
    reasons.appendChild(li)
  })
  if (!d.reasons || !d.reasons.length) reasons.innerHTML = `<li class="mono">none</li>`

  const per = el("perCategory")
  per.innerHTML = ""
  const pcs = d.metadata && d.metadata.per_category_scores ? d.metadata.per_category_scores : []
  pcs.forEach(p => {
    const div = document.createElement("div")
    div.className = "catCard"
    const b = p.band || "—"
    const mc = p.matched_count ?? 0
    const sev = p.severity ?? "—"
    div.innerHTML = `
      <div class="catTop">
        <div class="catName">${p.category}</div>
        <div class="catMeta">
          <div class="badge ${bandClass(b)}">${b}</div>
          <div class="mono">${fmt(p.score)}</div>
        </div>
      </div>
      <div class="catLine">severity: <span class="mono">${fmt(sev)}</span> • matched: <span class="mono">${mc}</span></div>
      <div class="chips">
        ${(p.matched_reasons || []).map(x => `<div class="chip">${x}</div>`).join("") || `<div class="chip mono">none</div>`}
      </div>
    `
    per.appendChild(div)
  })
  if (!pcs.length) per.innerHTML = `<div class="catCard"><div class="catName">—</div><div class="catLine">No per-category scores</div></div>`

  const ev = el("evidence")
  ev.innerHTML = ""
  const groups = groupEvidence(d.evidence || [])
  groups.forEach(([k, items], idx) => {
    const wrap = document.createElement("div")
    wrap.className = "evGroup"

    const head = document.createElement("div")
    head.className = "evHead"
    head.innerHTML = `<span>${k.toUpperCase()} engine</span><span class="mono">${items.length}</span>`

    const body = document.createElement("div")
    body.className = "evBody" + (idx === 0 ? " open" : "")
    body.innerHTML = items.map(e => {
      const desc = e.description || ""
      const meta = e.metadata ? JSON.stringify(e.metadata) : ""
      const val = e.value ? JSON.stringify(e.value) : ""
      return `
        <div class="evRow">
          <div>${desc}</div>
          ${val ? `<div class="evVal mono">${val}</div>` : ""}
          ${meta ? `<div class="evSmall mono">${meta}</div>` : ""}
        </div>
      `
    }).join("")

    head.addEventListener("click", () => {
      body.classList.toggle("open")
    })

    wrap.appendChild(head)
    wrap.appendChild(body)
    ev.appendChild(wrap)
  })
  if (!groups.length) ev.innerHTML = `<div class="evGroup"><div class="evHead"><span>—</span></div></div>`

  const exp = resp && resp.explanation ? resp.explanation : null
  if (exp && typeof exp === "object") {
    if (typeof exp.text === "string" && exp.text.trim()) {
      el("explain").textContent = exp.text
    } else {
      el("explain").textContent = JSON.stringify(exp, null, 2)
    }
  } else {
    el("explain").textContent = "No AI explanation available for this decision."
  }
}

const addRun = (payload, resp) => {
  const d = resp && resp.decision ? resp.decision : {}
  const item = {
    ts: new Date().toISOString(),
    category: d.risk_category || "—",
    band: d.metadata && d.metadata.risk_band ? d.metadata.risk_band : "—",
    score: d.risk_score,
    audit_id: resp.audit_id,
    payload,
    resp
  }
  state.runs.unshift(item)
  state.runs = state.runs.slice(0, 10)
  renderHistory()
}

const renderHistory = () => {
  const h = el("history")
  h.innerHTML = ""
  if (!state.runs.length) {
    h.innerHTML = `<div class="hItem"><div class="hLeft"><div>no runs yet</div><div class="hSmall">run history will appear here</div></div></div>`
    return
  }
  state.runs.forEach((r, i) => {
    const div = document.createElement("div")
    div.className = "hItem"
    div.innerHTML = `
      <div class="hLeft">
        <div><span class="mono">#${i+1}</span> • ${r.category} • <span class="badge ${bandClass(r.band)}">${r.band}</span> • <span class="mono">${fmt(r.score)}</span></div>
        <div class="hSmall">${r.ts} • audit_id=${r.audit_id || "—"}</div>
      </div>
      <div class="hRight">
        <button class="hBtn" data-act="load">Load</button>
        <button class="hBtn" data-act="json">Copy JSON</button>
      </div>
    `
    div.querySelector('[data-act="load"]').addEventListener("click", () => {
      loadPayload(r.payload)
      render(r.resp)
      toast("loaded")
    })
    div.querySelector('[data-act="json"]').addEventListener("click", async () => {
      await navigator.clipboard.writeText(JSON.stringify(r.resp, null, 2))
      toast("copied response")
    })
    h.appendChild(div)
  })
}

const loadPayload = (p) => {
  const f = p.fraud || {}
  el("txn_amount").value = f.txn_amount ?? ""
  el("txn_currency").value = f.txn_currency ?? ""
  el("txn_country").value = f.txn_country ?? ""
  el("avg_txn_amount_30d").value = f.avg_txn_amount_30d ?? ""
  el("txns_1h").value = f.txns_1h ?? ""
  el("txns_24h").value = f.txns_24h ?? ""
  el("account_age_days").value = f.account_age_days ?? ""
  el("device_change_7d").value = f.device_change_7d ?? ""
  el("failed_logins_24h").value = f.failed_logins_24h ?? ""

  const t = p.text || {}
  el("case_id").value = t.case_id ?? ""
  el("channel").value = t.channel ?? ""
  el("customer_id").value = t.customer_id ?? ""
  el("text").value = t.text ?? ""
}

const examplePayload = () => ({
  fraud: {
    txn_amount: 1200,
    txn_currency: "GBP",
    txn_country: "GB",
    avg_txn_amount_30d: 120,
    txns_1h: 6,
    txns_24h: 40,
    account_age_days: 30,
    device_change_7d: 1,
    failed_logins_24h: 3
  },
  text: {
    case_id: "C-1001",
    channel: "chat",
    customer_id: "U-1",
    text: "I complained twice and I feel stressed and anxious because I was misled"
  }
})

const call = async (path, opts) => {
  const res = await fetch(path, opts)
  const txt = await res.text()
  let data = null
  try { data = txt ? JSON.parse(txt) : null } catch { data = txt }
  if (!res.ok) throw new Error((data && data.detail) ? JSON.stringify(data.detail) : `HTTP ${res.status}`)
  return data
}

const score = async () => {
  setStatus("scoring...")
  const payload = buildPayload()

  try {
    const resp = await call(api.scoreExplain, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    })
    render(resp)
    addRun(payload, resp)
    toast("scored")
    setStatus("")
  } catch (e) {
    setStatus("error")
    toast(String(e.message || e))
  }
}

const copyCurl = async () => {
  const payload = buildPayload()
  const cmd = `curl -s -X POST "http://127.0.0.1:8000${api.scoreExplain}" -H "Content-Type: application/json" -d '${JSON.stringify(payload)}'`
  await navigator.clipboard.writeText(cmd)
  toast("copied cURL")
}

const copyJson = async () => {
  const payload = buildPayload()
  await navigator.clipboard.writeText(JSON.stringify(payload, null, 2))
  toast("copied json")
}

const ping = async (path, name) => {
  try {
    const d = await call(path, { method: "GET" })
    toast(`${name}: ok`)
    setStatus("")
    return d
  } catch (e) {
    toast(`${name}: fail`)
    setStatus("error")
  }
}

const clearAll = () => {
  loadPayload({ fraud: {}, text: {} })
  el("rawJson").textContent = "{}"
  el("finalCategory").textContent = "—"
  el("riskBand").className = "badge"
  el("riskBand").textContent = "—"
  el("riskScore").textContent = "—"
  el("severityLine").textContent = ""
  el("reasons").innerHTML = ""
  el("perCategory").innerHTML = ""
  el("evidence").innerHTML = ""
  el("metaLine").textContent = "No runs yet"
  el("explain").textContent = "No AI explanation available for this decision."
  toast("cleared")
}

const init = () => {
  el("apiPath").textContent = api.scoreExplain

  el("btnScore").addEventListener("click", score)
  el("btnCopyCurl").addEventListener("click", copyCurl)
  el("btnCopyJson").addEventListener("click", copyJson)

  el("btnHealth").addEventListener("click", () => ping(api.health, "health"))
  el("btnReady").addEventListener("click", () => ping(api.ready, "ready"))

  el("btnLoadExample").addEventListener("click", () => {
    loadPayload(examplePayload())
    toast("example loaded")
  })

  el("btnClear").addEventListener("click", clearAll)

  renderHistory()
}

init()