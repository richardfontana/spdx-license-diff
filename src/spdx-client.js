// SPDX-FileCopyrightText: SPDX-License-Diff contributors
// SPDX-License-Identifier: GPL-3.0-or-later

const BASE_LICENSE_URL = 'https://spdx.org/licenses/';
const LIST_URLS = {
  licenses: `${BASE_LICENSE_URL}licenses.json`,
  exceptions: `${BASE_LICENSE_URL}exceptions.json`
};

async function fetchJson(url) {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Request failed (${response.status}) for ${url}`);
  }
  return response.json();
}

function normalizeDetailsUrl(detailsUrl) {
  if (/^(?:[a-z]+:)?\/\//i.test(detailsUrl)) {
    return detailsUrl.replace('http:', 'https:').replace(/\.html$/i, '.json');
  }

  return `${BASE_LICENSE_URL}${detailsUrl}`.replace(/\.html$/i, '.json');
}

async function mapConcurrent(items, worker, concurrency = 10) {
  const results = new Array(items.length);
  let index = 0;

  const runners = Array.from({ length: Math.min(concurrency, items.length) }, async () => {
    while (index < items.length) {
      const current = index;
      index += 1;
      results[current] = await worker(items[current], current);
    }
  });

  await Promise.all(runners);
  return results;
}

export async function downloadSpdxCorpus({ includeExceptions = true, concurrency = 10 } = {}) {
  const categories = includeExceptions ? ['licenses', 'exceptions'] : ['licenses'];
  const corpus = [];

  for (const category of categories) {
    const list = await fetchJson(LIST_URLS[category]);
    const items = list[category] || [];

    const loaded = await mapConcurrent(items, async (item) => {
      const details = await fetchJson(normalizeDetailsUrl(item.detailsUrl));

      const idKey = category === 'licenses' ? 'licenseId' : 'licenseExceptionId';
      const textKey = category === 'licenses' ? 'licenseText' : 'licenseExceptionText';

      return {
        id: details[idKey] || item[idKey],
        name: details.name || item.name,
        text: details[textKey] || '',
        category,
        reference: details.seeAlso?.[0] || `${BASE_LICENSE_URL}${item.reference || ''}`
      };
    }, concurrency);

    corpus.push(...loaded.filter((entry) => entry.text));
  }

  return corpus;
}
