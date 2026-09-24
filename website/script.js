// Definisi field numerik (input text)
const FIELDS_INPUT = [
  { id: 'suhu-min',             label: 'Temperatur terendah (°C)',        isNumeric: true  },
  { id: 'suhu-max',             label: 'Temperatur tertinggi (°C)',        isNumeric: true  },
  { id: 'suhu-rata',            label: 'Rata rata Temperatur (°C)',        isNumeric: true  },
  { id: 'kelembapan',           label: 'Rata rata kelembapan (%)',         isNumeric: true  },
  { id: 'curah-hujan',          label: 'Curah Hujan (mm)',                 isNumeric: true  },
  { id: 'durasi-matahari',      label: 'Durasi matahari/cerah (jam)',      isNumeric: true  },
  { id: 'angin-max',            label: 'Kecepatan angin tertinggi (m/s)', isNumeric: true  },
  { id: 'arah-angin-max',       label: 'Arah Angin tertinggi (°)',         isNumeric: true  },
  { id: 'angin-rata',           label: 'Rata-rata kecepatan Angin (m/s)', isNumeric: true  },
  { id: 'arah-angin-terbanyak', label: 'Arah angin terbanyak (°)',         isNumeric: false },
];

// Definisi dropdown (select)
const FIELDS_SELECT = [
  { id: 'model-prediksi', label: 'Model Prediksi' },
  { id: 'nama-daerah',    label: 'Nama Daerah'    },
];

// Gabungan semua field untuk label di ringkasan hasil
const LABEL_MAP = {
  'model-prediksi':      'Model Prediksi',
  'suhu-min':            'Temperatur terendah (°C)',
  'suhu-max':            'Temperatur tertinggi (°C)',
  'suhu-rata':           'Rata rata Temperatur (°C)',
  'kelembapan':          'Rata rata kelembapan (%)',
  'curah-hujan':         'Curah Hujan (mm)',
  'durasi-matahari':     'Durasi matahari/cerah (jam)',
  'angin-max':           'Kecepatan angin tertinggi (m/s)',
  'arah-angin-max':      'Arah Angin tertinggi (°)',
  'angin-rata':          'Rata-rata kecepatan Angin (m/s)',
  'arah-angin-terbanyak':'Arah angin terbanyak (°)',
  'nama-daerah':         'Nama Daerah',
};

// Referensi elemen DOM
const form      = document.getElementById('form-prediksi');
const btnReset  = document.getElementById('btn-reset');
const result    = document.getElementById('result');
const resultIsi = document.getElementById('result-isi');

// Normalise desimal: ganti koma dengan titik agar parseFloat bekerja
function normalizeAngka(str) {
  return str.trim().replace(',', '.');
}

// Cek apakah string merupakan angka valid (bilangan riil)
function isAngkaValid(str) {
  const normalized = normalizeAngka(str);
  return normalized !== '' && !isNaN(parseFloat(normalized)) && isFinite(normalized);
}

// Tampilkan pesan error pada elemen tertentu (input atau select)
function tampilkanError(id, pesan) {
  const el   = document.getElementById(id);
  const span = el.nextElementSibling;
  el.classList.add('input--error');
  span.textContent = pesan;
}

// Bersihkan error semua field
function bersihkanError() {
  [...FIELDS_INPUT, ...FIELDS_SELECT].forEach(({ id }) => {
    const el   = document.getElementById(id);
    const span = el.nextElementSibling;
    el.classList.remove('input--error');
    span.textContent = '';
  });
}

// Validasi semua field; kembalikan true jika lolos
function validasiForm() {
  let valid = true;

  // Validasi dropdown
  FIELDS_SELECT.forEach(({ id, label }) => {
    const el = document.getElementById(id);
    if (!el.value) {
      tampilkanError(id, `${label} wajib dipilih.`);
      valid = false;
    }
  });

  // Validasi input teks
  FIELDS_INPUT.forEach(({ id, label, isNumeric }) => {
    const el    = document.getElementById(id);
    const nilai = el.value.trim();

    if (nilai === '') {
      tampilkanError(id, `${label} wajib diisi.`);
      valid = false;
    } else if (isNumeric && !isAngkaValid(nilai)) {
      tampilkanError(id, `${label} harus berupa angka valid.`);
      valid = false;
    }
  });

  return valid;
}

// Kumpulkan semua nilai ke satu object
function kumpulkanData() {
  const data = {};

  // Dropdown
  FIELDS_SELECT.forEach(({ id }) => {
    data[id] = document.getElementById(id).value;
  });

  // Input teks
  FIELDS_INPUT.forEach(({ id, isNumeric }) => {
    const nilai = document.getElementById(id).value.trim();
    data[id] = isNumeric ? parseFloat(normalizeAngka(nilai)) : nilai;
  });

  return data;
}

// TODO: Hubungkan model prediksi di sini (Linear Regression / Decision Tree / KNN)
// data.model-prediksi berisi 'lr', 'dt', atau 'knn'
function predictFlood(data) {
  // TODO: implementasi model prediksi berdasarkan data['model-prediksi']
  // Contoh: return { status: 'Banjir', probabilitas: 0.87 };
  return null;
}

// Label ramah untuk nilai model
const MODEL_LABEL = { lr: 'Linear Regression', dt: 'Decision Tree', knn: 'K-Nearest Neighbors (KNN)' };

// Tampilkan ringkasan input di area #result
function tampilkanHasil(data) {
  const urutan = ['model-prediksi', ...FIELDS_INPUT.map(f => f.id), 'nama-daerah'];

  const baris = urutan.map(id => {
    let nilai = data[id];
    if (id === 'model-prediksi') nilai = MODEL_LABEL[nilai] || nilai;
    return `<div><strong>${LABEL_MAP[id]}:</strong> ${nilai}</div>`;
  }).join('');

  resultIsi.innerHTML = baris;
  result.hidden = false;
}

// Event: submit form
form.addEventListener('submit', function (e) {
  e.preventDefault();
  bersihkanError();
  result.hidden = true;

  if (!validasiForm()) return;

  const data = kumpulkanData();
  predictFlood(data);
  tampilkanHasil(data);
});

// Event: tombol Reset
btnReset.addEventListener('click', function () {
  form.reset();
  bersihkanError();
  result.hidden = true;
  resultIsi.innerHTML = '';
});
