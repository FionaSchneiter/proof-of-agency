# Proof of Autonomous Agency (PoA)
## Protocol Specification v0.1

**Status:** Experimental / Research Specification  
**Version:** 0.1  
**Date:** 2026-09-27

**License (Specification):** CC0-1.0 / CC-BY-4.0  
**License (Code & Circuits):** Apache-2.0 / MIT


---

## 1. Abstract

This specification defines **Proof of Autonomous Agency (PoA)**, a protocol for cryptographically proving that a specific action was generated and executed by an attested software agent from an attested prior state, in response to an authenticated observation, under an authorized policy.

The protocol deliberately does **not** attempt to prove that a system is "intelligent", "conscious", or metaphysically an AI. Instead, it defines a technically verifiable notion of agency:

> An action is attributable to an agent when the action is cryptographically bound to an attested agent implementation, a prior committed state, a new authenticated observation, an authorized policy, and an execution path that excludes unauthorized external intervention.

The protocol combines:

- public-key agent identity,
- hardware / runtime attestation,
- state commitments,
- authenticated observations,
- zero-knowledge proofs,
- policy enforcement,
- capability-gated tool execution,
- monotonic execution counters,
- tamper-evident execution receipts.

---

## 2. Scope

Proof of Agents (PoA) is engineered for secure agent-to-agent and agent-to-service interactions, providing verifiers with robust evidence that goes beyond simple behavioral imitation.

Key Use Cases
- Autonomous Networks: Peer-to-peer communication between independent software agents.
- Financial & Smart Contracts: Automated execution of financial transactions and agreements.
- Enterprise Delegation: Securely authorized actions performed by agents on behalf of organizations.
- Machine-to-Machine (M2M): Standardized authorization for connected systems and devices.
- Research & Tool Use: Autonomous agents conducting research or operating external APIs and tools.
- Privacy-Preserving Verification: Validating agent behavior without exposing underlying sensitive data.

What PoA Leaves Agnostic
As a flexible framework, PoA does not mandate:
- A specific AI model architecture
- A particular Trusted Execution Environment (TEE) vendor
- A specific zero-knowledge (ZK) proof system
- A particular blockchain network
- A universal definition of intelligence or consciousness


---

## 3. Terminology

| Term | Definition |
|---|---|
| Agent | Software system claiming autonomous agency |
| Verifier | Entity requesting and validating a PoA proof |
| Model | Computational model used by the agent |
| Runtime | Software environment executing the model and policy |
| State | Persistent internal state relevant to future actions |
| Observation | New externally supplied or observed information |
| Policy | Formal constraints governing agent behavior |
| Action | Intended external operation |
| Tool | External service or API invoked by an agent |
| Action Gate | Trusted component controlling external execution |
| TEE | Trusted Execution Environment |
| Commitment | Cryptographic binding to hidden data |
| ZK Proof | Zero-knowledge proof of a computation/relation |
| Epoch | Bounded period during which a specific autonomy configuration applies |
| Receipt | Signed evidence that an authorized action was executed |
| Nonce | Fresh verifier-generated challenge value |

---

# 4. Security Goal

A successful PoA proof establishes the following statement:

> There exists an authenticated agent implementation `M`, state `S`, observation `O`, and policy `P` such that the agent's registered commitments match those values, the action `A` is the valid result of executing `M` on `S` and `O` under `P`, the state transition is valid, the challenge is fresh, and the resulting action was authorized and executed through the agent's protected execution path.

Formally:

\[
R(M,S,O,P,A,N)=1
\]

where:

\[
A = F(M,S,O,P,N)
\]

and the public commitments satisfy:

\[
H(M)=M_H
\]

\[
H(P)=P_H
\]

\[
Commit(S)=C_S
\]

\[
H(O)=O_H
\]

\[
H(A)=A_H
\]

The verifier learns only the public values and the validity of the proof unless additional disclosure is explicitly required.

---

# 5. Security Model

PoA provides evidence for four separate properties.

## 5.1 Identity Binding

The public key identifies the registered agent instance.

\[
K_{pub} \leftrightarrow AgentID
\]

## 5.2 Implementation Binding

The agent's execution environment is bound to a registered model/runtime/policy measurement.

\[
H(M)=M_H
\]

\[
H(Runtime)=R_H
\]

\[
H(P)=P_H
\]

## 5.3 Decision Binding

The action is cryptographically bound to:

- the previous state;
- the new observation;
- the policy;
- the model/runtime;
- the verifier's challenge.

## 5.4 Execution Binding

The externally visible action can only be executed after the Action Gate verifies the relevant proof and issues an execution capability.

This prevents a valid proof from being generated for an action that is subsequently replaced by a different action.

---

# 6. Trust Model

The protocol assumes a trust root for at least:

1. the agent's identity;
2. the hardware/TEE attestation mechanism;
3. the verifier's policy authority;
4. the cryptographic algorithms.

A deployment may use:

- a centralized certificate authority;
- a decentralized registry;
- an organizational PKI;
- a DID-based registry;
- a consortium trust root.

PoA itself does not mandate one trust model.

---

# 7. Cryptographic Primitives

A conforming implementation MUST provide equivalents of:

```text
H(x)             collision-resistant hash
Sign(sk, m)      digital signature
Verify(pk,m,sig) signature verification
Commit(x,r)      hiding/binding commitment
Prove(R,w)       zero-knowledge proof
VerifyZK(R,x,π)   zero-knowledge proof verification
Random(n)        cryptographically secure randomness
```

Recommended primitives:

```text
Hash:       SHA-256 or SHA-3-256
Signature:  Ed25519 or an equivalent post-quantum-capable scheme
ZK:         SNARK/STARK family appropriate to deployment
Encoding:   CBOR or canonical JSON
```

Production deployments SHOULD consider post-quantum signatures and hybrid key exchange.

---

# 8. Agent Registration

An agent is registered with:

```text
AgentRecord {
    agent_id
    public_key
    model_hash
    runtime_hash
    policy_hash
    capabilities
    tee_attestation
    issuer
    validity_period
}
```

Example:

```json
{
  "agent_id": "agent:A17",
  "public_key": "base64(...)",
  "model_hash": "sha256:91ab...",
  "runtime_hash": "sha256:3f21...",
  "policy_hash": "sha256:71fe...",
  "capabilities": [
    "search",
    "email"
  ],
  "tee_attestation": "base64(...)"
}
```

The registration authority verifies the TEE attestation and binds the agent public key to the measured execution environment.

---

# 9. State Commitment

The agent maintains a sequence of state commitments.

Initial state:

\[
C_0 = Commit(S_0,r_0)
\]

For each subsequent transition:

\[
C_{i+1}=H(C_i \parallel A_i \parallel S_{i+1}^{commit})
\]

A verifier does not need access to the actual state.

The commitment provides continuity and prevents arbitrary retroactive state substitution.

---

# 10. Observation Authentication

An observation SHOULD originate from an authenticated source where possible.

Example:

```text
Observation {
    observation_id
    source_id
    payload_hash
    timestamp
    sequence
    source_signature
}
```

The agent computes:

\[
O_H=H(O)
\]

The ZK proof binds the decision to `O_H`.

For observations without an external signature, the protocol can still prove that the observation was part of the agent's execution, but cannot independently establish that the observation itself was truthful.

---

# 11. Challenge Protocol

The verifier generates a fresh nonce:

\[
N \leftarrow Random(256)
\]

and sends:

```text
PoAChallenge {
    protocol_version
    agent_id
    nonce
    requested_policy_hash
    requested_capability
    expiry
}
```

The nonce MUST NOT be reused within its validity domain.

The agent MUST bind the nonce into:

- the ZK proof;
- the action commitment;
- the execution capability;
- the execution receipt.

This prevents replay of old proofs.

---

# 12. Autonomy Epoch

The agent operates within an autonomy epoch.

```text
Epoch {
    epoch_id
    start_time
    end_time
    policy_hash
    allowed_tools
    allowed_actions
    human_override
    external_control_channels
}
```

Example:

```json
{
  "epoch_id": "731",
  "start_time": "2026-09-27T10:00:00Z",
  "end_time": "2026-09-27T10:30:00Z",
  "policy_hash": "sha256:71fe...",
  "allowed_tools": ["search", "email"],
  "human_override": false,
  "external_control_channels": []
}
```

The TEE or equivalent trusted execution layer MUST bind actions to the current epoch.

---

# 13. ZK Relation

The core relation is:

\[
R_{PoA}(x,w)=1
\]

### Public input `x`

```text
agent_id
model_hash
runtime_hash
policy_hash
previous_state_commitment
observation_hash
action_hash
nonce
epoch_id
action_counter
```

### Private witness `w`

```text
model
runtime_state
policy
state
observation
randomness
intermediate_execution_state
```

The circuit verifies:

```text
1. H(model) == model_hash

2. H(policy) == policy_hash

3. H(runtime) == runtime_hash

4. Commit(state) == previous_state_commitment

5. H(observation) == observation_hash

6. action == Execute(model, state, observation, policy)

7. PolicyAllows(policy, action)

8. H(action) == action_hash

9. nonce is included in the computation

10. state transition is valid

11. epoch is valid

12. action_counter is valid
```

The actual model execution may be represented directly in the ZK circuit or by a recursive/verifiable-computation construction.

---

# 14. Model Execution

The abstract execution function is:

\[
(S_{i+1},A_i)=F(M,S_i,O_i,P,N)
\]

The protocol does not require the verifier to know the internal algorithm.

For large AI models, directly proving the full neural-network inference in a conventional SNARK may be computationally expensive.

A production implementation MAY therefore use:

- recursive proofs;
- lookup arguments;
- verifiable inference;
- proof-carrying inference;
- GPU/TEE co-processing;
- STARK-based computation proofs;
- specialized ML proving systems.

The protocol is agnostic to the proving backend.

---

# 15. Action Gate

The Action Gate is the critical execution-binding component.

An agent MUST NOT directly invoke protected external tools.

Instead:

```text
Agent
  |
  | ActionIntent + ZK Proof
  v
Action Gate
  |
  | verify proof
  | verify nonce
  | verify policy
  | verify epoch
  | verify counter
  v
Capability Token
  |
  v
Tool
```

The capability token contains:

```text
Capability {
    agent_id
    action_hash
    nonce
    epoch_id
    tool_id
    counter
    expiry
    signature
}
```

The tool MUST verify that the capability authorizes exactly the action being executed.

---

# 16. Execution Receipt

After execution, the tool produces:

```text
ExecutionReceipt {
    agent_id
    action_hash
    tool_id
    result_hash
    nonce
    epoch_id
    action_counter
    timestamp
    tool_signature
}
```

This creates the chain:

\[
Observation
\rightarrow
Decision
\rightarrow
ZKProof
\rightarrow
Capability
\rightarrow
Execution
\rightarrow
Receipt
\]

---

# 17. Complete Protocol Flow

```text
Verifier                         Agent
   |                               |
   |---- PoA Challenge ----------->|
   |                               |
   |                         authenticate O
   |                               |
   |                         execute M
   |                               |
   |                         compute A
   |                               |
   |                         generate π
   |                               |
   |<----- π + commitments --------|
   |                               |
   | verify ZK proof                |
   | verify attestation             |
   |                               |
   |                               |
   |                    Action Gate |
   |                         |      |
   |                         | verify
   |                         v
   |                       Tool
   |                         |
   |                    Execution
   |                         |
   |                    Receipt
   |                               |
   |<------- Receipt --------------|
```

---

# 18. Agent-to-Agent Example

Agent A wants to send Agent B a recommendation.

Agent B sends:

```json
{
  "type": "PoAChallenge",
  "agent_id": "agent:A",
  "nonce": "8f31...",
  "requested_capability": "recommendation",
  "expiry": "2026-09-27T10:05:00Z"
}
```

Agent A processes new observations and generates:

```text
Action:
    recommendation = R
```

Agent A returns:

```json
{
  "agent_id": "agent:A",
  "model_hash": "sha256:91ab...",
  "policy_hash": "sha256:71fe...",
  "state_commitment": "sha256:83cd...",
  "observation_hash": "sha256:4a91...",
  "action_hash": "sha256:11ac...",
  "nonce": "8f31...",
  "epoch_id": "731",
  "action_counter": 1842,
  "zk_proof": "base64(...)",
  "attestation": "base64(...)"
}
```

Agent B verifies:

```text
VerifyZK(...) == true
VerifyAttestation(...) == true
VerifySignature(...) == true
nonce == expected_nonce
policy_hash == authorized_policy
epoch == valid_epoch
counter == expected_counter
```

Agent B can therefore establish the PoA claim without seeing Agent A's internal state.

---

# 19. Threat Model

## 19.1 Replay Attack

**Attack:** attacker reuses a valid old proof.

**Mitigation:**

- fresh nonce;
- expiry;
- monotonic counter;
- epoch binding.

---

## 19.2 Action Substitution

**Attack:** valid proof exists for action A, but attacker executes action B.

**Mitigation:**

\[
H(A)=ActionHash
\]

and the Action Gate signs only the exact action hash.

---

## 19.3 State Rewriting

**Attack:** agent claims a different internal state after the fact.

**Mitigation:**

state commitments chained through execution counters.

---

## 19.4 Human Injection

**Attack:** human changes the action after model execution.

**Mitigation:**

- trusted Action Gate;
- capability-gated tools;
- no external control channel during autonomous epochs;
- hardware-protected signing key.

---

## 19.5 Script Impersonation

**Attack:** a deterministic script pretends to be an AI agent.

**Result:**

PoA intentionally does NOT prevent this.

If the registered implementation is the script, the proof may be completely valid.

Therefore PoA proves **attested agency**, not intelligence.

---

## 19.6 Compromised Observation Source

**Attack:** the input source lies.

**Mitigation:**

source authentication and signed observations.

Important limitation:

> Authenticity of an observation does not imply truthfulness of the observation.

---

## 19.7 Compromised TEE

**Attack:** hardware/runtime attestation is compromised.

**Mitigation:**

- hardware vendor trust roots;
- independent attestation;
- measured boot;
- key rotation;
- optional multi-party attestation.

PoA cannot provide stronger guarantees than its hardware/root-of-trust assumptions.

---

# 20. What PoA Does Not Prove

PoA does NOT prove:

- consciousness;
- intelligence;
- sentience;
- correctness of the model;
- truth of observations;
- good intentions;
- absence of all bugs;
- absence of physical compromise;
- that the model is a neural network;
- that the system is economically or legally an "agent";
- that the action was optimal.

The protocol proves a narrower property:

> A specified computational process produced and executed a specified action under specified constraints.

---

# 21. Agency Levels

A deployment SHOULD distinguish three levels.

## PoI — Proof of Identity

Proves:

> "I control Agent A."

Evidence:

- public key;
- certificate;
- signature.

## PoE — Proof of Execution

Proves:

> "Agent A executed computation X."

Evidence:

- attestation;
- execution proof;
- model/runtime hash.

## PoA — Proof of Agency

Proves:

> "Agent A generated action A from its committed prior state and authenticated observation under policy P and executed that action through its protected execution path."

Evidence:

- identity;
- attestation;
- state commitment;
- observation binding;
- ZK proof;
- capability;
- execution receipt.

---

# 22. Privacy Properties

A verifier SHOULD NOT need access to:

- model weights
- prompts
- private memory
- chain-of-thought
- private observations
- intermediate activations
- confidential tool results

The proof SHOULD reveal only the minimum information necessary to establish the requested claim.

Selective disclosure MAY reveal:

```text
policy_id
capability
action class
risk class
time interval
```

without revealing the underlying private state.

---

# 23. Delegation

Agents MAY delegate authority.

Example:

```text
Agent A
   |
   | delegates capability C
   v
Agent B
   |
   | executes C
   v
Tool
```

A delegation token SHOULD contain:

```text
Delegation {
    issuer
    delegate
    capability
    scope
    max_depth
    expiry
    nonce
    issuer_signature
}
```

The PoA proof MUST bind the delegation chain when the action depends on delegated authority.

---

# 24. Revocation

Agents SHOULD support revocation of:

- identity keys;
- model versions;
- policies;
- tool capabilities;
- epochs.

A revocation record MAY be:

```text
Revocation {
    subject
    reason
    effective_at
    issuer
    signature
}
```

Verifiers MUST check revocation status before accepting a PoA proof when the deployment requires real-time revocation.

---

# 25. Versioning

Every PoA message MUST include:

```text
protocol_version
```

Example:

```text
"poa/0.1"
```

The ZK circuit identifier SHOULD also be included:

```text
circuit_id
circuit_version
```

This prevents ambiguity when the agent model, policy language, or proving system changes.

---

# 26. Canonical Serialization

All data committed or signed MUST use canonical serialization.

CBOR with deterministic encoding is RECOMMENDED.

Hash inputs SHOULD be domain separated:

```text
H("PoA:model:" || model_bytes)
H("PoA:state:" || state_bytes)
H("PoA:action:" || action_bytes)
H("PoA:observation:" || observation_bytes)
H("PoA:receipt:" || receipt_bytes)
```

This prevents cross-protocol hash confusion.

---

# 27. Reference Message Types

Minimum message set:

```text
AgentRegistration
PoAChallenge
PoAProof
CapabilityToken
ExecutionReceipt
DelegationToken
RevocationRecord
```

---

# 28. Minimal PoA Proof Object

```json
{
  "protocol": "poa/0.1",
  "agent_id": "agent:A17",
  "circuit_id": "poa-transformer-v1",
  "model_hash": "sha256:...",
  "runtime_hash": "sha256:...",
  "policy_hash": "sha256:...",
  "previous_state_commitment": "sha256:...",
  "observation_hash": "sha256:...",
  "action_hash": "sha256:...",
  "nonce": "base64...",
  "epoch_id": "731",
  "action_counter": 1842,
  "zk_proof": "base64...",
  "tee_attestation": "base64..."
}
```

---

# 29. Verification Algorithm

Conceptually:

```text
verifyPoA(proof, challenge):

    assert proof.protocol == supported_version
    assert proof.agent_id == challenge.agent_id
    assert proof.nonce == challenge.nonce
    assert current_time < challenge.expiry
    verify_agent_registration(proof.agent_id)

    verify_tee_attestation(
        proof.tee_attestation,
        proof.agent_id,
        proof.model_hash,
        proof.runtime_hash
    )

    verify_zk_proof(
        circuit_id = proof.circuit_id,
        public_inputs = {
            proof.agent_id,
            proof.model_hash,
            proof.runtime_hash,
            proof.policy_hash,
            proof.previous_state_commitment,
            proof.observation_hash,
            proof.action_hash,
            proof.nonce,
            proof.epoch_id,
            proof.action_counter
        },
        proof = proof.zk_proof
    )

    assert authorized_policy(proof.policy_hash)

    assert valid_epoch(proof.epoch_id)

    assert valid_counter(
        proof.agent_id,
        proof.action_counter
    )

    return VALID
```

---

# 30. Reference Action Gate Algorithm

```text
authorize(action, proof):

    verifyPoA(proof)
    assert hash(action) == proof.action_hash
    assert action.tool_id in current_epoch.allowed_tools

    capability = Sign(
        agent_private_key,
        {
            agent_id,
            action_hash,
            nonce,
            epoch_id,
            action_counter,
            expiry
        }
    )

    return capability
```

The tool verifies:

```text
verify(capability)

assert capability.action_hash == hash(received_action)
assert capability.tool_id == received_action.tool_id
assert not expired(capability)
assert not replayed(capability)
```

---

# 31. Fundamental Limitation

The strongest claim that PoA can make is not:

> "This entity is an AI."

It is:

> "This action was produced and executed by the computational process represented by this attested agent identity, under the specified state, observation, policy, and execution constraints."

This distinction is essential.

- A deterministic program can satisfy PoA.
- A neural network can satisfy PoA.
- A hybrid symbolic/neural system can satisfy PoA.
- A human-operated system can satisfy PoA **if the human is permitted by the policy and execution architecture**.

Therefore a deployment that wants "autonomy" MUST explicitly define:

```text
allowed_human_intervention
allowed_external_control
allowed_delegation
allowed_model_updates
allowed_state_updates
```

---

# 32. Recommended Strong-Autonomy Profile

For a strict autonomous-agent profile:

```text
human_override = false
external_control_channels = []
model_update = forbidden_during_epoch
policy_update = forbidden_during_epoch
state_reset = forbidden_during_epoch
action_gate = mandatory
hardware_attestation = mandatory
fresh_nonce = mandatory
state_chain = mandatory
execution_receipt = mandatory
```

This profile provides the strongest practical form of PoA described by this specification.

---

# 33. Open Research Problems

Several parts remain research-intensive.

### 33.1 Efficient ZK inference

Proving large transformer inference efficiently remains expensive.

### 33.2 Stateful recursive proofs

Long-lived agents require scalable recursive state proofs.

### 33.3 Behavioral continuity

A valid attestation at time `t0` does not automatically prove that the same behavioral constraints remained valid indefinitely.

### 33.4 Model updates

Updating an agent's model changes the computational identity.

A new model MUST therefore receive a new measurement/version.

### 33.5 Truth of observations

PoA proves use of an observation, not truth of the observation.

### 33.6 Formal autonomy

"Autonomous" must be reduced to explicit machine-verifiable constraints.

### 33.7 Hardware trust

TEE compromise can undermine the strongest protocol-level guarantees.

---

# 34. Design Principle

The central design principle is:

\[
\boxed{
Identity
+
Attestation
+
State
+
Observation
+
Computation
+
Policy
+
Execution
}
\]

must form one cryptographically continuous chain.

A proof that establishes only identity is insufficient.

A proof that establishes only model execution is insufficient.

A proof that establishes only policy compliance is insufficient.

A genuine PoA requires binding all of them to the **same concrete action**.

---

# 35. Summary

PoA v0.1 defines an operational notion of autonomous agency:

\[
\boxed{
A_i =
F(M,S_i,O_i,P,N)
}
\]

with:

\[
C_{i+1}=Commit(S_{i+1})
\]

and:

\[
H(A_i)=A_H
\]

followed by:

\[
Capability(A_H)
\rightarrow
Execution
\rightarrow
Receipt
\]

The verifier can therefore establish:

1. **which agent identity acted;**
2. **which implementation was attested;**
3. **which policy governed the action;**
4. **which committed state preceded the action;**
5. **which authenticated observation was used;**
6. **that the action satisfies the policy;**
7. **that the proof corresponds to a fresh challenge;**
8. **that the exact action was authorized;**
9. **that the exact action was executed through the protected path.**

It does not attempt to prove consciousness or intelligence.

That restriction is a feature, not a weakness: it turns an otherwise philosophical question into a cryptographically testable protocol.

---

## Appendix A — Conceptual Security Claim

A successful PoA proof establishes:

\[
\exists M,S,O,P:
\]

\[
H(M)=M_H
\]

\[
Commit(S)=C_S
\]

\[
H(O)=O_H
\]

\[
A=F(M,S,O,P,N)
\]

\[
PolicyAllows(P,A)=true
\]

\[
Capability(A)=valid
\]

\[
ExecutionReceipt(A)=valid
\]

subject to the security assumptions of the cryptographic primitives, attestation root, execution environment, and policy authority.

---

## Appendix B — Terminology Recommendation

The term **"Proof of Agency"** should be used carefully.

A more precise terminology for implementations is:

> **Proof of Cryptographically Verifiable Autonomous Execution (PCVAE)**

"Proof of Agency" is shorter and more useful as the protocol family name, while PCVAE describes the actual security property being proven.

---

**End of Specification — PoA v0.1**
