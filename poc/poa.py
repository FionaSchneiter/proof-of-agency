'''Small, explicitly non-production PoA v0.1 reference implementation.

Uses Ed25519-signed, canonical JSON claims. This is a transparent signed
attestation, not a zero-knowledge proof or hardware/runtime attestation.
'''
from __future__ import annotations

import json
import base64
import secrets
import hashlib
import time
from dataclasses import asdict, dataclass
from typing import Any, Callable

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(domain: str, value: Any) -> str:
    return "sha256:" + hashlib.sha256(domain.encode() + b"\0" + canonical(value)).hexdigest()


def transition_commit(previous: str, action: dict[str, Any], next_state: dict[str, Any]) -> str:
    state_hash = digest("PoA:state", next_state)
    return digest("PoA:state-transition", {"previous": previous, "action": action, "next_state": state_hash})


def public_key_b64(key: Ed25519PublicKey) -> str:
    return base64.b64encode(key.public_bytes(Encoding.Raw, PublicFormat.Raw)).decode("ascii")


@dataclass(frozen=True)
class Challenge:
    protocol: str
    agent_id: str
    nonce: str
    policy_hash: str
    capability: str
    expires_at: int


@dataclass(frozen=True)
class Proof:
    claims: dict[str, Any]
    signature: str


@dataclass(frozen=True)
class CapabilityToken:
    claims: dict[str, Any]
    signature: str


@dataclass(frozen=True)
class ExecutionReceipt:
    claims: dict[str, Any]
    signature: str


class Agent:
    '''Agent with committed state, action function and Ed25519 identity'''

    def __init__(self, agent_id: str, policy: dict[str, Any], initial_state: dict[str, Any],
                 decide: Callable[[dict[str, Any], dict[str, Any]], tuple[dict[str, Any], dict[str, Any]]]):
        self.agent_id = agent_id
        self.policy = policy
        self.policy_hash = digest("PoA:policy", policy)
        self.state = initial_state
        self.counter = 0
        self._key = Ed25519PrivateKey.generate()
        self._decide = decide
        self.state_commitment = digest("PoA:state", initial_state)

    @property
    def public_key(self) -> str:
        return public_key_b64(self._key.public_key())

    def create_proof(self, challenge: Challenge, observation: dict[str, Any]) -> Proof:
        if challenge.agent_id != self.agent_id or challenge.policy_hash != self.policy_hash:
            raise ValueError("Challenge does not match this agent or its policy")
        if int(time.time()) >= challenge.expires_at:
            raise ValueError("Challenge expired")
        previous = self.state_commitment
        action, next_state = self._decide(self.state, observation)
        if not isinstance(action, dict) or not isinstance(next_state, dict):
            raise TypeError("decide must return (action dict, next_state dict)")
        next_commitment = transition_commit(previous, action, next_state)
        self.counter += 1
        claims = {
            "protocol": "poa/0.1", "agent_id": self.agent_id,
            "public_key": self.public_key, "model_hash": self.policy.get("model_hash", "sha256:demo"),
            "runtime_hash": digest("PoA:runtime", "python-poc"), "policy_hash": self.policy_hash,
            "previous_state_commitment": previous, "next_state": next_state,
            "next_state_commitment": next_commitment, "observation": observation,
            "observation_hash": digest("PoA:observation", observation), "action": action,
            "action_hash": digest("PoA:action", action), "nonce": challenge.nonce,
            "epoch_id": self.policy.get("epoch_id", "demo"), "action_counter": self.counter,
            "issued_at": int(time.time()), "capability": challenge.capability,
        }
        proof = Proof(claims, base64.b64encode(self._key.sign(canonical(claims))).decode("ascii"))
        self.state = next_state
        self.state_commitment = next_commitment
        return proof


class Verifier:
    '''Tracks registered identities, policy, expected state/counter and nonces'''

    def __init__(self, policy: dict[str, Any], ttl_seconds: int = 60):
        self.policy = policy
        self.policy_hash = digest("PoA:policy", policy)
        self.ttl_seconds = ttl_seconds
        self.agents: dict[str, dict[str, Any]] = {}
        self.pending: dict[str, Challenge] = {}
        self.used: set[str] = set()

    def register(self, agent: Agent) -> None:
        self.agents[agent.agent_id] = {
            "public_key": agent.public_key,
            "state_commitment": digest("PoA:state", agent.state),
            "counter": 0,
        }

    def challenge(self, agent_id: str, capability: str) -> Challenge:
        if agent_id not in self.agents:
            raise ValueError("Unknown agent")
        if capability not in self.policy.get("allowed_capabilities", []):
            raise ValueError("Capability is not authorized")
        c = Challenge("poa/0.1", agent_id, secrets.token_urlsafe(32), self.policy_hash,
                      capability, int(time.time()) + self.ttl_seconds)
        self.pending[c.nonce] = c
        return c

    def verify(self, proof: Proof, challenge: Challenge) -> dict[str, Any]:
        p = proof.claims
        expected = self.pending.get(challenge.nonce)
        if expected != challenge or challenge.nonce in self.used:
            raise ValueError("Unknown, consumed, or mismatched nonce")
        if int(time.time()) >= challenge.expires_at:
            raise ValueError("Challenge expired")
        if p.get("protocol") != "poa/0.1" or p.get("agent_id") != challenge.agent_id:
            raise ValueError("Protocol or agent identity mismatch")
        registered = self.agents.get(challenge.agent_id)
        if not registered or p.get("public_key") != registered["public_key"]:
            raise ValueError("Unregistered signing key")
        Ed25519PublicKey.from_public_bytes(base64.b64decode(registered["public_key"], validate=True)).verify(
            base64.b64decode(proof.signature, validate=True), canonical(p))
        if p.get("nonce") != challenge.nonce or p.get("policy_hash") != self.policy_hash or challenge.policy_hash != self.policy_hash:
            raise ValueError("Nonce or policy mismatch")
        if p.get("capability") != challenge.capability or p.get("capability") not in self.policy.get("allowed_capabilities", []):
            raise ValueError("Capability mismatch or denied")
        if p.get("previous_state_commitment") != registered["state_commitment"]:
            raise ValueError("State chain mismatch")
        if transition_commit(p["previous_state_commitment"], p.get("action"), p.get("next_state")) != p.get("next_state_commitment"):
            raise ValueError("Invalid next-state commitment")
        if digest("PoA:observation", p.get("observation")) != p.get("observation_hash"):
            raise ValueError("Observation hash mismatch")
        action = p.get("action")
        if digest("PoA:action", action) != p.get("action_hash"):
            raise ValueError("Action hash mismatch")
        if action.get("tool_id") != challenge.capability or action.get("type") not in self.policy.get("allowed_actions", []):
            raise ValueError("Action is outside policy")
        if p.get("action_counter") != registered["counter"] + 1:
            raise ValueError("Counter is not the expected next value")

        # Consume and advance atomically only after every check succeeds.
        self.used.add(challenge.nonce)
        del self.pending[challenge.nonce]
        registered["counter"] = p["action_counter"]
        registered["state_commitment"] = p["next_state_commitment"]
        return p

    def sign_capability(self, claims: dict[str, Any], gate_key: Ed25519PrivateKey) -> CapabilityToken:
        body = {"agent_id": claims["agent_id"], "action_hash": claims["action_hash"],
                "nonce": claims["nonce"], "epoch_id": claims["epoch_id"],
                "tool_id": claims["action"]["tool_id"], "counter": claims["action_counter"],
                "expiry": int(time.time()) + self.ttl_seconds}
        return CapabilityToken(body, base64.b64encode(gate_key.sign(canonical(body))).decode("ascii"))


class ActionGate:
    '''Executes only an action that was verified and bound to a gate capability'''

    def __init__(self, verifier: Verifier):
        self.verifier = verifier
        self._key = Ed25519PrivateKey.generate()
        self.executed: set[str] = set()

    def authorize_and_execute(self, proof: Proof, challenge: Challenge,
                              tools: dict[str, Callable[[dict[str, Any]], Any]]) -> tuple[Any, ExecutionReceipt]:
        claims = self.verifier.verify(proof, challenge)
        token = self.verifier.sign_capability(claims, self._key)
        action = claims["action"]
        t = token.claims
        Ed25519PublicKey.from_public_bytes(self._key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)).verify(
            base64.b64decode(token.signature, validate=True), canonical(t))
        if t["action_hash"] != digest("PoA:action", action) or t["tool_id"] != action["tool_id"]:
            raise ValueError("Capability does not authorize this exact action")
        if int(time.time()) >= t["expiry"] or t["nonce"] in self.executed:
            raise ValueError("Expired or replayed capability")
        tool = tools.get(t["tool_id"])
        if tool is None:
            raise ValueError("No tool registered for authorized tool_id")
        result = tool(action)
        self.executed.add(t["nonce"])
        receipt_claims = {"agent_id": t["agent_id"], "action_hash": t["action_hash"],
                          "tool_id": t["tool_id"], "result_hash": digest("PoA:result", result),
                          "nonce": t["nonce"], "epoch_id": t["epoch_id"], "action_counter": t["counter"],
                          "timestamp": int(time.time())}
        receipt = ExecutionReceipt(receipt_claims,
            base64.b64encode(self._key.sign(canonical(receipt_claims))).decode("ascii"))
        return result, receipt


def demo() -> None:
    policy = {"allowed_capabilities": ["demo.echo"], "allowed_actions": ["echo"], "epoch_id": "local-demo"}
    agent = Agent("agent:demo", policy, {"steps": 0},
                  lambda state, obs: ({"tool_id": "demo.echo", "type": "echo", "payload": obs["message"]},
                                     {"steps": state["steps"] + 1}))
    verifier = Verifier(policy)
    verifier.register(agent)
    challenge = verifier.challenge(agent.agent_id, "demo.echo")
    proof = agent.create_proof(challenge, {"message": "hello PoA"})
    result, receipt = ActionGate(verifier).authorize_and_execute(
        proof, challenge, {"demo.echo": lambda action: {"echo": action["payload"]}})
    print(json.dumps({"result": result, "receipt": asdict(receipt)}, indent=2))



if __name__ == "__main__":
    demo()
