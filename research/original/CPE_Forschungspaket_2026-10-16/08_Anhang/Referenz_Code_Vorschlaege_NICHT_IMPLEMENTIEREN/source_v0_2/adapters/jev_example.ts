/**
 * Jev integration illustration. REQUIRES TYPESAFE_API_KEY; never hands Jev broker control.
 * Vendor endpoint: https://api.typesafe.ai/v1/systemone
 * Runtime: Node 20+ with native fetch. Example not executed in this sandbox.
 */
const apiKey = process.env.TYPESAFE_API_KEY;
if (!apiKey) throw new Error('Set TYPESAFE_API_KEY');

// Only verified and timestamped short evidence summaries should reach Jev.
const state = {
  as_of: '2026-10-16T06:00:00Z',
  source_url: 'https://example.org/research-example',
  evidence_summary: 'SYNTHETIC EXAMPLE: customer qualification documented',
};
const response = await fetch('https://api.typesafe.ai/v1/systemone', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${apiKey}`, 'Content-Type': 'application/json' },
  body: JSON.stringify({
    model: 'jev-latest',
    state,
    questions: {
      contains_dated_primary_evidence: {
        type: 'noul',
        instructions: 'Does the provided evidence contain a date and a traceable primary-source claim?',
      },
      evidence_type: {
        type: 'choice',
        instructions: 'Classify the type of new information; do not make a trade decision.',
        criteria: {
          customer_qualification: 'A customer qualified a new product',
          new_contract: 'A signed customer order or contract',
          capacity_plan: 'Announced production capacity or factory expansion',
          unsupported_marketing: 'Unverified advertising or promotional claim',
        },
      },
    },
  }),
});
if (!response.ok) throw new Error(`Jev HTTP ${response.status}`);
const result: unknown = await response.json();
console.log(JSON.stringify(result, null, 2));
// Do not treat Jev probabilities as calibrated real-world investment probabilities.
