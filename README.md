# Proof of Autonomous Agency (PoA)

## Objective
Proof of Autonomous Agency (PoA) is a cryptographic protocol for the tamper-proof verifiability of autonomous software actions. It seamlessly proves that an action was generated and executed by a specific, attested agent from a defined prior state, based on verified inputs, and in compliance with authorized policies.

## Core Mechanisms
- **Cryptographic Binding:** Tamper-proofly links identity, hardware attestation (TEE), prior state ($S$), observation ($O$), policy ($P$), and execution path.
- **Zero-Knowledge Proofs (ZKP):** Prove correct policy compliance and state logic without disclosing confidential model weights, prompts, or internal memory contents.
- **Decoupled Execution (Action Gate):** Separating decision-making from actual execution. External interfaces and tools only execute actions after the Action Gate validates the mathematical proof and a fresh single-use token (nonce).

## Key Distinction
PoA proves neither "intelligence" nor "consciousness". It serves exclusively as proof of a cryptographically verifiable autonomous execution (Proof of Cryptographically Verifiable Autonomous Execution, PCVAE) free from unauthorized interference.

---
---

# Proof of Autonomous Agency (PoA) - Deutsch

## Zielsetzung
Proof of Autonomous Agency (PoA) ist ein kryptographisches Protokoll zur fälschungssicheren Nachweisbarkeit autonomer Software-Aktionen. Es belegt lückenlos, dass eine Handlung von einem spezifischen, attestierten Agenten aus einem definierten Vorzustand auf Basis verifizierter Eingaben und unter Einhaltung autorisierter Regelwerke (Policies) generiert und ausgeführt wurde.

## Kernmechanismen
- **Kryptographische Bindung:** Verknüpft Identität, Hardware-Attestierung (TEE), Vorzustand ($S$), Beobachtung ($O$), Policy ($P$) und Ausführungspfad fälschungssicher miteinander.
- **Zero-Knowledge-Proofs (ZKP):** Beweisen die korrekte Regeltreue und Zustandslogik, ohne vertrauliche Modellgewichtungen, Prompts oder interne Speicherinhalte offenzulegen.
- **Entkoppelte Ausführung (Action Gate):** Trennt die Entschlussfassung von der tatsächlichen Ausführung. Externe Schnittstellen und Werkzeuge führen Aktionen erst aus, nachdem das Action Gate den mathematischen Proof sowie ein frisches Einmal-Token (Nonce) validiert hat.

## Wesentliche Abgrenzung
PoA beweist weder "Intelligenz" noch "Bewusstsein". Es dient ausschließlich als Nachweis einer kryptographisch verifizierbaren, autonomen Ausführung (Proof of Cryptographically Verifiable Autonomous Execution, PCVAE) frei von unbefugten Eingriffen.
