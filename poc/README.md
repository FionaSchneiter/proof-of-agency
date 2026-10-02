# PoA v0.1 Python PoC

Minimaler lokaler Referenzablauf für Agent, Verifier und Action Gate.

## Start

Benötigt Python 3.10+ und `cryptography`:

```powershell
py -m pip install -r requirements.txt
py poa.py
```

Der Demo-Agent bildet eine Observation auf eine `echo`-Action ab. Der Verifier
prüft Ed25519-Signatur, einmalige Challenge/Nonce, Ablaufzeit, Policy, Action-
Hash, verketteten State-Commit und monotone Action-Counter. Das Action Gate
führt erst danach das exakt gebundene Action-Objekt aus und gibt einen signierten
Receipt zurück.

## Sicherheitsgrenzen

Dies ist ein PoC, keine produktionsreife PoA-Implementierung:

- Die `Proof`-Claims sind signierte, offenliegende JSON-Daten; es gibt keinen
  Zero-Knowledge-Proof. Verifier erhalten State und Observation.
- Model- und Runtime-Messwerte sind Demo-Platzhalter; TEE-Attestierung,
  Registrierung durch eine Vertrauensstelle, Revocation und Epoch-Verwaltung
  fehlen.
- Nonce- und Counter-Speicher sind nur im Prozess und nicht crash-/clusterfest.
- Das Gate und seine Ed25519-Schlüssel liegen im selben Prozess. Die Isolation
  eines separaten vertrauenswürdigen Gates wird nicht demonstriert.
- Die Policy ist einfaches Python-Datenformat; keine formale Policy-Engine.

Die Implementierung demonstriert Protokoll-Bindungen und Replay-/Substitutions-
Prüfungen, beweist aber nicht, dass eine konkrete Modellberechnung korrekt
ausgeführt wurde.
