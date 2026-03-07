/* Politibase — Client-side interactivity */

const API = '/api';

/* ── Ballot Lookup ────────────────────────────────────────────── */

async function lookupBallot() {
    const input = document.getElementById('address-input');
    const results = document.getElementById('ballot-results');
    const address = input.value.trim();

    if (!address) {
        results.innerHTML = '<p class="subtitle">Please enter an address.</p>';
        return;
    }

    results.innerHTML = '<p class="subtitle">Looking up your ballot...</p>';

    try {
        const resp = await fetch(`${API}/ballot/lookup?address=${encodeURIComponent(address)}`);
        const data = await resp.json();
        renderBallotResults(data, results);
    } catch (err) {
        results.innerHTML = `<p class="subtitle" style="color: var(--red-600)">Error: ${err.message}</p>`;
    }
}

function renderBallotResults(data, container) {
    if (!data.local_data || data.local_data.length === 0) {
        container.innerHTML = `
            <div class="detail-section">
                <h3>No local data found</h3>
                <p class="bio">We don't have data for this address yet. Politibase currently covers the Fargo-Moorhead metro area (Moorhead MN, Fargo ND, Clay County MN, Cass County ND).</p>
            </div>`;
        return;
    }

    let html = '';

    for (const jur of data.local_data) {
        const typeBadge = badgeClass(jur.jurisdiction.type);
        html += `
        <div class="jurisdiction-section">
            <h3>
                <span class="badge ${typeBadge}">${jur.jurisdiction.type.replace('_', ' ')}</span>
                ${jur.jurisdiction.name}
            </h3>`;

        if (jur.offices.length === 0) {
            html += '<p class="subtitle">No offices on record.</p>';
        }

        html += '<div class="card-grid">';
        for (const office of jur.offices) {
            for (const holder of office.current_holders) {
                html += `
                <div class="card">
                    <h3><a href="/candidate/${holder.id}">${holder.name}</a></h3>
                    <div class="subtitle">${office.title}${office.district ? ' — ' + office.district : ''}</div>
                    ${holder.occupation ? `<div class="bio">${holder.occupation}</div>` : ''}
                    <span class="badge badge-incumbent">Incumbent</span>
                </div>`;
            }

            for (const elec of office.upcoming_elections) {
                html += `
                <div class="card" style="border-left: 3px solid var(--yellow-600)">
                    <h3>${office.title}</h3>
                    <div class="subtitle">Upcoming Election: ${elec.date}</div>
                    <div class="bio">${elec.description || ''}</div>
                    ${elec.filing_deadline ? `<div class="subtitle">Filing deadline: ${elec.filing_deadline}</div>` : ''}
                </div>`;
            }
        }
        html += '</div></div>';
    }

    container.innerHTML = html;
}

function badgeClass(type) {
    switch (type) {
        case 'city': return 'badge-city';
        case 'county': return 'badge-county';
        case 'school_district': return 'badge-school_district';
        case 'judicial_district': return 'badge-judicial_district';
        case 'conservation_district': return 'badge-conservation_district';
        case 'park_district': return 'badge-park_district';
        default: return '';
    }
}

/* ── Candidate Search ─────────────────────────────────────────── */

async function searchCandidates() {
    const input = document.getElementById('candidate-search');
    const results = document.getElementById('candidate-results');
    const query = input.value.trim();

    if (!query) {
        loadAllCandidates();
        return;
    }

    try {
        const resp = await fetch(`${API}/candidates/?search=${encodeURIComponent(query)}`);
        const data = await resp.json();
        renderCandidateList(data, results);
    } catch (err) {
        results.innerHTML = `<p>Error: ${err.message}</p>`;
    }
}

async function loadAllCandidates() {
    const results = document.getElementById('candidate-results');
    if (!results) return;

    try {
        const resp = await fetch(`${API}/candidates/`);
        const data = await resp.json();
        renderCandidateList(data, results);
    } catch (err) {
        results.innerHTML = `<p>Error loading candidates: ${err.message}</p>`;
    }
}

async function filterByJurisdiction(jurisdictionId) {
    const results = document.getElementById('candidate-results');
    const url = jurisdictionId
        ? `${API}/candidates/?jurisdiction_id=${jurisdictionId}`
        : `${API}/candidates/`;
    try {
        const resp = await fetch(url);
        const data = await resp.json();
        renderCandidateList(data, results);
    } catch (err) {
        results.innerHTML = `<p>Error: ${err.message}</p>`;
    }
}

function renderCandidateList(candidates, container) {
    if (candidates.length === 0) {
        container.innerHTML = '<p class="subtitle">No candidates found.</p>';
        return;
    }

    let html = '<div class="card-grid">';
    for (const c of candidates) {
        html += `
        <div class="card">
            <h3><a href="/candidate/${c.id}">${c.full_name}</a></h3>
            ${c.occupation ? `<div class="subtitle">${c.occupation}</div>` : ''}
            ${c.residence_city ? `<div class="bio">${c.residence_city}${c.residence_state ? ', ' + c.residence_state : ''}</div>` : ''}
        </div>`;
    }
    html += '</div>';
    container.innerHTML = html;
}

/* ── Init ─────────────────────────────────────────────────────── */

document.addEventListener('DOMContentLoaded', () => {
    // Ballot search: submit on Enter
    const addrInput = document.getElementById('address-input');
    if (addrInput) {
        addrInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') lookupBallot();
        });
    }

    // Candidate search: debounced
    const candInput = document.getElementById('candidate-search');
    if (candInput) {
        let timer;
        candInput.addEventListener('input', () => {
            clearTimeout(timer);
            timer = setTimeout(searchCandidates, 300);
        });
    }

    // Auto-load candidates list on candidates page
    if (document.getElementById('candidate-results')) {
        loadAllCandidates();
    }
});
